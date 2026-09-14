"""Grades de follow-up de Botox da aba Sale.

Três leituras independentes sobre os mesmos dados:

1. /api/crm/botox/vencidos    — Botox realizados há 5 meses ou mais (contatar)
2. /api/crm/botox/m5          — disparos M5 registrados pelo pipeline externo (n8n)
3. /api/crm/botox/recorrentes — pacientes com duas ou mais aplicações

Nenhum endpoint escreve. Todos respeitam o escopo do médico logado.
"""

from datetime import datetime, time, timedelta
from urllib.parse import quote

from dateutil.relativedelta import relativedelta
from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required

from models import (
    CosmeticProcedurePlan,
    MessageDispatch,
    Note,
    Patient,
    ProcedureExecution,
    db,
)
from services.clinic_time import clinic_today
from services.followup_service import FOLLOWUP_MONTHS_BOTOX


botox_followup_bp = Blueprint('botox_followup', __name__)

DEFAULT_WINDOW_DAYS = 90
MAX_ROWS = 500

FOLLOWUP_STATUS_LABELS = {
    'pendente': 'sem resposta',
    'contatado': 'contatado',
    'agendado': 'agendou',
    'sem_resposta': 'sem resposta',
}


def _digits(value):
    return ''.join(character for character in (value or '') if character.isdigit())


def _whatsapp_url(patient, message):
    phone = _digits(patient.phone)
    if not phone:
        return None
    return f'https://wa.me/{phone}?text={quote(message)}'


def _iso(value):
    return value.isoformat() if value else None


def _as_date(value):
    """Aceita date ou datetime e devolve sempre date."""
    return value.date() if hasattr(value, 'date') else value


def _botox_query():
    """Execuções de Botox realizadas, já no escopo do médico logado."""
    query = (
        db.session.query(ProcedureExecution, CosmeticProcedurePlan, Note, Patient)
        .join(CosmeticProcedurePlan, ProcedureExecution.plan_id == CosmeticProcedurePlan.id)
        .join(Note, CosmeticProcedurePlan.note_id == Note.id)
        .join(Patient, Note.patient_id == Patient.id)
        .filter(
            ProcedureExecution.execution_status == 'realizada',
            ProcedureExecution.performed_date.isnot(None),
            db.func.lower(CosmeticProcedurePlan.procedure_name).like('%botox%'),
        )
    )
    if current_user.is_doctor():
        query = query.filter(Note.doctor_id == current_user.id)
    return query


def _followup_date_for(execution):
    """Usa a data gravada e calcula somente como fallback."""
    if execution.followup_date:
        return _as_date(execution.followup_date)
    return _as_date(
        execution.performed_date + relativedelta(months=FOLLOWUP_MONTHS_BOTOX)
    )


def _group_by_patient_day(rows):
    """Agrupa execuções por paciente e dia; duas no mesmo dia contam como uma."""
    groups = {}
    for execution, _plan, _note, patient in rows:
        performed = _as_date(execution.performed_date)
        key = (patient.id, performed)
        group = groups.setdefault(key, {
            'patient': patient,
            'performed_date': performed,
            'followup_date': None,
            'execution_ids': [],
            'followup_status': None,
        })
        group['execution_ids'].append(execution.id)
        if group['followup_date'] is None:
            group['followup_date'] = _followup_date_for(execution)
        if group['followup_status'] is None and execution.followup_status:
            group['followup_status'] = execution.followup_status
    return groups


def _m5_dispatch_map(patient_ids):
    """Dispatches M5 indexados por paciente e data de vencimento."""
    if not patient_ids:
        return {}
    dispatches = (
        db.session.query(MessageDispatch)
        .filter(
            MessageDispatch.patient_id.in_(patient_ids),
            MessageDispatch.message_type == 'm5',
        )
        .all()
    )
    return {
        (dispatch.patient_id, dispatch.due_at): dispatch
        for dispatch in dispatches
    }


def _m5_cell(dispatch, patient):
    if dispatch is None:
        if not patient.accepts_marketing:
            return {'status': 'sem_optin', 'label': 'sem opt-in', 'sent_at': None}
        return {'status': None, 'label': '—', 'sent_at': None}

    labels = {
        'enviada': 'enviada',
        'falhou': 'falhou',
        'pendente': 'pendente',
        'pulada': 'pulada',
    }
    label = labels.get(dispatch.status, dispatch.status)
    if dispatch.status == 'enviada' and dispatch.sent_at:
        label = f'enviada {dispatch.sent_at.strftime("%d/%m")}'
    return {
        'status': dispatch.status,
        'label': label,
        'sent_at': _iso(dispatch.sent_at),
    }


@botox_followup_bp.route('/api/crm/botox/vencidos')
@login_required
def botox_vencidos():
    """Botox cujo follow-up de 5 meses já venceu — uma linha por paciente."""
    today = clinic_today()
    groups = _group_by_patient_day(_botox_query().all())

    latest = {}
    for group in groups.values():
        patient = group['patient']
        if not _digits(patient.phone):
            continue
        if group['followup_date'] > today:
            continue
        current = latest.get(patient.id)
        if current is None or group['performed_date'] > current['performed_date']:
            latest[patient.id] = group

    dispatch_map = _m5_dispatch_map(list(latest.keys()))
    result = []
    for group in latest.values():
        patient = group['patient']
        followup_date = group['followup_date']
        dispatch = dispatch_map.get((patient.id, followup_date))
        overdue_days = (today - followup_date).days
        first_name = (patient.name or '').split(' ')[0]

        result.append({
            'patient_id': patient.id,
            'patient_name': patient.name,
            'phone': patient.phone,
            'execution_ids': group['execution_ids'],
            'performed_date': _iso(group['performed_date']),
            'followup_date': _iso(followup_date),
            'overdue_days': overdue_days,
            'severity': 'alta' if overdue_days >= 60 else (
                'media' if overdue_days >= 30 else 'baixa'
            ),
            'accepts_marketing': bool(patient.accepts_marketing),
            'm5': _m5_cell(dispatch, patient),
            'whatsapp_url': _whatsapp_url(
                patient,
                f'Olá {first_name}, tudo bem? Já faz 5 meses da sua aplicação de '
                f'Botox — quer agendar a próxima?',
            ),
        })

    result.sort(key=lambda row: row['overdue_days'], reverse=True)
    return jsonify({'rows': result[:MAX_ROWS], 'total': len(result)})


@botox_followup_bp.route('/api/crm/botox/m5')
@login_required
def botox_m5():
    """Disparos M5 registrados pelo pipeline externo."""
    try:
        window_days = int(request.args.get('days', DEFAULT_WINDOW_DAYS))
    except (TypeError, ValueError):
        window_days = DEFAULT_WINDOW_DAYS

    query = (
        db.session.query(MessageDispatch, Patient, ProcedureExecution)
        .join(Patient, Patient.id == MessageDispatch.patient_id)
        .outerjoin(
            ProcedureExecution,
            ProcedureExecution.id == MessageDispatch.execution_id,
        )
        .filter(MessageDispatch.message_type == 'm5')
    )

    if window_days > 0:
        cutoff = clinic_today() - timedelta(days=window_days)
        query = query.filter(MessageDispatch.due_at >= cutoff)

    status_filter = (request.args.get('status') or '').strip()
    if status_filter:
        query = query.filter(MessageDispatch.status == status_filter)

    if current_user.is_doctor():
        query = (
            query.join(
                CosmeticProcedurePlan,
                CosmeticProcedurePlan.id == ProcedureExecution.plan_id,
            )
            .join(Note, Note.id == CosmeticProcedurePlan.note_id)
            .filter(Note.doctor_id == current_user.id)
        )

    rows = query.order_by(MessageDispatch.due_at.desc()).all()

    def _sort_key(row):
        dispatch = row[0]
        if dispatch.sent_at:
            return (1, dispatch.sent_at)
        return (0, datetime.combine(dispatch.due_at, time.min))

    rows.sort(key=_sort_key, reverse=True)
    counters = {'enviada': 0, 'falhou': 0, 'pendente': 0, 'pulada': 0}

    result = []
    for dispatch, patient, execution in rows:
        counters[dispatch.status] = counters.get(dispatch.status, 0) + 1
        first_name = (patient.name or '').split(' ')[0]
        followup_status = execution.followup_status if execution else None

        result.append({
            'dispatch_id': dispatch.id,
            'patient_id': patient.id,
            'patient_name': patient.name,
            'phone': patient.phone,
            'due_at': _iso(dispatch.due_at),
            'sent_at': _iso(dispatch.sent_at),
            'status': dispatch.status,
            'last_error': dispatch.last_error,
            'retorno': FOLLOWUP_STATUS_LABELS.get(followup_status, '—'),
            'retorno_status': followup_status,
            'whatsapp_url': _whatsapp_url(
                patient,
                f'Olá {first_name}, tudo bem?',
            ),
        })

    return jsonify({
        'rows': result[:MAX_ROWS],
        'total': len(result),
        'counters': counters,
        'window_days': window_days,
    })


@botox_followup_bp.route('/api/crm/botox/recorrentes')
@login_required
def botox_recorrentes():
    """Pacientes com duas ou mais aplicações de Botox."""
    try:
        min_count = max(2, int(request.args.get('min', 2)))
    except (TypeError, ValueError):
        min_count = 2

    today = clinic_today()
    groups = _group_by_patient_day(_botox_query().all())

    by_patient = {}
    for group in groups.values():
        patient = group['patient']
        entry = by_patient.setdefault(patient.id, {
            'patient': patient,
            'dates': [],
        })
        entry['dates'].append(group['performed_date'])

    total_patients = len(by_patient)
    result = []
    for entry in by_patient.values():
        dates = sorted(set(entry['dates']))
        if len(dates) < min_count:
            continue

        patient = entry['patient']
        gaps = [
            (dates[index + 1] - dates[index]).days
            for index in range(len(dates) - 1)
        ]
        avg_gap_months = round(sum(gaps) / len(gaps) / 30.44, 1) if gaps else None
        months_since_last = round((today - dates[-1]).days / 30.44, 1)
        first_name = (patient.name or '').split(' ')[0]

        result.append({
            'patient_id': patient.id,
            'patient_name': patient.name,
            'phone': patient.phone,
            'count': len(dates),
            'dates': [value.isoformat() for value in dates],
            'last_date': dates[-1].isoformat(),
            'avg_gap_months': avg_gap_months,
            'months_since_last': months_since_last,
            'whatsapp_url': _whatsapp_url(
                patient,
                f'Olá {first_name}, tudo bem?',
            ),
        })

    result.sort(key=lambda row: (row['count'], row['last_date']), reverse=True)
    counts = [row['count'] for row in result]
    gaps = [row['avg_gap_months'] for row in result if row['avg_gap_months']]

    return jsonify({
        'rows': result[:MAX_ROWS],
        'total': len(result),
        'total_botox_patients': total_patients,
        'avg_applications': round(sum(counts) / len(counts), 1) if counts else 0,
        'median_gap_months': sorted(gaps)[len(gaps) // 2] if gaps else None,
    })