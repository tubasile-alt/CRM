"""Endpoints de integração para o pipeline externo de mensagens.

As três travas são independentes e permanecem desligadas por padrão:

1. INTEGRATIONS_API_KEY ausente bloqueia todas as rotas com 503.
2. DISPATCH_SEND_MODE controla off, test e live.
3. DISPATCH_DAILY_CAP limita a quantidade diária no servidor.

Este módulo não envia mensagens. Ele somente expõe a fila e registra o
resultado informado pelo integrador externo.
"""

import os
import secrets
from datetime import timedelta
from functools import wraps

from flask import Blueprint, jsonify, request
from sqlalchemy import and_, or_

from services.clinic_time import clinic_today, get_brazil_time


integrations_bp = Blueprint(
    'integrations',
    __name__,
    url_prefix='/api/integrations',
)

DEFAULT_DAILY_CAP = 20
DEFAULT_RESERVATION_TTL = 30
MAX_PAGE_SIZE = 50
VALID_SEND_MODES = frozenset({'off', 'test', 'live'})


def _api_key_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        expected = os.environ.get('INTEGRATIONS_API_KEY')
        if not expected:
            return jsonify({'error': 'integração não configurada'}), 503

        provided = request.headers.get('X-API-Key', '')
        if not secrets.compare_digest(provided, expected):
            return jsonify({'error': 'não autorizado'}), 401

        return view(*args, **kwargs)

    return wrapper


def _send_mode():
    mode = (os.environ.get('DISPATCH_SEND_MODE') or 'off').strip().lower()
    return mode if mode in VALID_SEND_MODES else 'off'


def _test_phones():
    raw = os.environ.get('DISPATCH_TEST_PHONES') or ''
    return {
        ''.join(character for character in item if character.isdigit())
        for item in raw.split(',')
        if item.strip()
    }


def _daily_cap():
    try:
        return max(0, int(os.environ.get(
            'DISPATCH_DAILY_CAP',
            DEFAULT_DAILY_CAP,
        )))
    except (TypeError, ValueError):
        return DEFAULT_DAILY_CAP


def _reservation_ttl():
    """Minutes until an abandoned reservation returns to the queue."""
    try:
        return max(1, int(os.environ.get(
            'DISPATCH_RESERVATION_TTL_MINUTES',
            DEFAULT_RESERVATION_TTL,
        )))
    except (TypeError, ValueError):
        return DEFAULT_RESERVATION_TTL


def _sent_today():
    from models import MessageDispatch, db

    return db.session.query(db.func.count(MessageDispatch.id)).filter(
        MessageDispatch.status == 'enviada',
        db.func.date(MessageDispatch.sent_at) == clinic_today(),
    ).scalar() or 0


def _consumed_today():
    """Count sent and currently reserved dispatches against the daily cap."""
    from models import MessageDispatch, db

    today = clinic_today()
    return db.session.query(db.func.count(MessageDispatch.id)).filter(
        or_(
            and_(
                MessageDispatch.status == 'enviada',
                db.func.date(MessageDispatch.sent_at) == today,
            ),
            and_(
                MessageDispatch.status == 'reservada',
                db.func.date(MessageDispatch.reserved_at) == today,
            ),
        )
    ).scalar() or 0


def _pending_query():
    """Dispatches vencidos de pacientes com telefone e consentimento."""
    from models import MessageDispatch, Patient, db

    return (
        db.session.query(MessageDispatch, Patient)
        .join(Patient, Patient.id == MessageDispatch.patient_id)
        .filter(
            MessageDispatch.status == 'pendente',
            MessageDispatch.due_at <= clinic_today(),
            Patient.phone.isnot(None),
            Patient.phone != '',
            Patient.accepts_marketing.is_(True),
        )
        .order_by(MessageDispatch.due_at.asc(), MessageDispatch.id.asc())
    )


def _reclaim_stale_reservations():
    """Return reservations older than the configured TTL to the pending queue."""
    from models import MessageDispatch, db

    cutoff = get_brazil_time() - timedelta(minutes=_reservation_ttl())
    reclaimed = db.session.query(MessageDispatch).filter(
        MessageDispatch.status == 'reservada',
        MessageDispatch.reserved_at < cutoff,
    ).update(
        {'status': 'pendente', 'reserved_at': None},
        synchronize_session=False,
    )
    if reclaimed:
        db.session.commit()
    return reclaimed


def _lock_pending(limit):
    """Select eligible pending dispatches, skipping locked rows on PostgreSQL."""
    from models import MessageDispatch, Patient, db

    query = (
        db.session.query(MessageDispatch, Patient)
        .join(Patient, Patient.id == MessageDispatch.patient_id)
        .filter(
            MessageDispatch.status == 'pendente',
            MessageDispatch.due_at <= clinic_today(),
            Patient.phone.isnot(None),
            Patient.phone != '',
            Patient.accepts_marketing.is_(True),
        )
        .order_by(MessageDispatch.due_at.asc(), MessageDispatch.id.asc())
        .limit(limit)
    )

    if db.session.get_bind().dialect.name == 'postgresql':
        query = query.with_for_update(
            of=MessageDispatch,
            skip_locked=True,
        )

    return query.all()


def _reserve(dispatches):
    """Mark the selected rows as reserved in one transaction."""
    from models import db

    reserved_at = get_brazil_time()
    for dispatch in dispatches:
        dispatch.status = 'reservada'
        dispatch.reserved_at = reserved_at
    db.session.commit()


def _reservation_diagnostics():
    from models import MessageDispatch, db

    cutoff = get_brazil_time() - timedelta(minutes=_reservation_ttl())
    base_query = db.session.query(MessageDispatch).filter(
        MessageDispatch.status == 'reservada',
    )
    return (
        base_query.count(),
        base_query.filter(MessageDispatch.reserved_at < cutoff).count(),
    )


def _serialize(dispatch, patient):
    from services.google_sheets import format_phone_for_sheets

    return {
        'dispatch_id': dispatch.id,
        'message_type': dispatch.message_type,
        'execution_id': dispatch.execution_id,
        'patient_id': patient.id,
        'patient_name': patient.name,
        'phone': format_phone_for_sheets(patient.phone),
        'due_at': dispatch.due_at.isoformat(),
    }


def _requested_limit():
    try:
        requested = int(request.args.get('limit', MAX_PAGE_SIZE))
    except (TypeError, ValueError):
        requested = MAX_PAGE_SIZE
    return max(0, min(requested, MAX_PAGE_SIZE))


@integrations_bp.route('/messages/due', methods=['GET'])
@_api_key_required
def messages_due():
    """Fila de envio sujeita às três travas."""
    mode = _send_mode()
    if mode == 'off':
        return jsonify({
            'mode': 'off',
            'messages': [],
            'note': 'DISPATCH_SEND_MODE=off — nenhuma mensagem liberada',
        })

    _reclaim_stale_reservations()

    cap = _daily_cap()
    used = _consumed_today()
    remaining = max(0, cap - used)
    if remaining == 0:
        return jsonify({
            'mode': mode,
            'messages': [],
            'note': f'cap diário atingido ({used}/{cap})',
        })

    limit = min(_requested_limit(), remaining)
    if limit == 0:
        return jsonify({
            'mode': mode,
            'daily_cap': cap,
            'sent_today': _sent_today(),
            'messages': [],
        })

    rows = _lock_pending(limit * 3)

    if mode == 'test':
        allowed = {phone[-11:] for phone in _test_phones() if phone}
        if not allowed:
            return jsonify({
                'mode': 'test',
                'messages': [],
                'note': 'DISPATCH_TEST_PHONES vazio — nada liberado',
            })
        rows = [
            (dispatch, patient)
            for dispatch, patient in rows
            if ''.join(character for character in (patient.phone or '')
                        if character.isdigit())[-11:] in allowed
        ]

    selected = rows[:limit]
    _reserve([dispatch for dispatch, _patient in selected])

    return jsonify({
        'mode': mode,
        'daily_cap': cap,
        'sent_today': _sent_today(),
        'messages': [
            _serialize(dispatch, patient)
            for dispatch, patient in selected
        ],
    })


@integrations_bp.route('/messages/preview', methods=['GET'])
@_api_key_required
def messages_preview():
    """Diagnóstico somente leitura, ignorando modo e cap."""
    rows = _pending_query().all()
    reserved, stale_reserved = _reservation_diagnostics()
    by_type = {}
    for dispatch, _patient in rows:
        by_type[dispatch.message_type] = (
            by_type.get(dispatch.message_type, 0) + 1
        )

    return jsonify({
        'mode_atual': _send_mode(),
        'daily_cap': _daily_cap(),
        'sent_today': _sent_today(),
        'total_vencidos': len(rows),
        'por_tipo': by_type,
        'reservadas': reserved,
        'reservadas_vencidas': stale_reserved,
        'amostra': [
            _serialize(dispatch, patient)
            for dispatch, patient in rows[:10]
        ],
    })


@integrations_bp.route('/messages/<int:dispatch_id>', methods=['PATCH'])
@_api_key_required
def messages_update(dispatch_id):
    """Registra o resultado retornado pelo integrador externo."""
    from models import MessageDispatch, db

    data = request.get_json(silent=True) or {}
    new_status = (data.get('status') or '').strip()
    if new_status not in ('enviada', 'falhou'):
        return jsonify({
            'error': "status deve ser 'enviada' ou 'falhou'",
        }), 400

    dispatch = db.session.get(MessageDispatch, dispatch_id)
    if not dispatch:
        return jsonify({'error': 'dispatch não encontrado'}), 404

    if dispatch.status not in ('pendente', 'reservada'):
        return jsonify({
            'dispatch_id': dispatch.id,
            'status': dispatch.status,
            'note': 'já processado, sem alteração',
        })

    dispatch.status = new_status
    dispatch.reserved_at = None
    dispatch.sent_at = get_brazil_time() if new_status == 'enviada' else None
    dispatch.last_error = (data.get('error') or '')[:500] or None
    db.session.commit()

    return jsonify({
        'dispatch_id': dispatch.id,
        'status': dispatch.status,
    })


@integrations_bp.route('/botox-sheet/sync', methods=['POST'])
@_api_key_required
def botox_sheet_sync():
    """Gatilho autenticado da reconciliação da aba Botox."""
    from services.botox_sheet_service import run_botox_sheet_sync

    ok, message = run_botox_sheet_sync()
    return jsonify({
        'ok': ok,
        'message': message,
    }), (200 if ok else 500)