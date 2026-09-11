"""Reconciliação da aba Botox do Google Sheets a partir do banco.

A planilha é um espelho de leitura: reconstruída por completo a cada execução.
Nenhum caminho de request escreve nela.
"""

from collections import defaultdict, OrderedDict
import logging

from sqlalchemy import text

from services.message_dispatch_status import (
    DISPATCH_KNOWN_STATUSES,
    UNKNOWN_DISPATCH_STATUS,
)


ADVISORY_LOCK_KEY = 918273
BOTOX_MESSAGE_TYPES = frozenset({'d0', 'm5'})
logger = logging.getLogger(__name__)

# Quando uma linha representa mais de uma execução, o status mais acionável
# precisa prevalecer. Em especial, uma falha terminal nunca pode ser escondida
# por uma execução enviada anteriormente ou por um estado desconhecido.
_DISPATCH_STATUS_PRIORITY = {
    'falhou': 50,
    # Um estado desconhecido precisa ficar visível para não produzir um
    # resumo enganoso, mas uma falha terminal continua vencendo-o.
    UNKNOWN_DISPATCH_STATUS: 45,
    'reservada': 40,
    'pendente': 30,
    'enviada': 20,
    'cancelada': 10,
    'pulada': 5,
}


def _normalized_dispatch_status(dispatch):
    raw_status = getattr(dispatch, 'status', None)
    status = raw_status.strip() if isinstance(raw_status, str) else ''
    if status in DISPATCH_KNOWN_STATUSES:
        return status
    return UNKNOWN_DISPATCH_STATUS


def _unknown_status_value(dispatch):
    raw_status = getattr(dispatch, 'status', None)
    value = raw_status.strip() if isinstance(raw_status, str) else ''
    return value or '(vazio)'


def _alert_unknown_dispatches(dispatches):
    """Registra o diagnóstico mínimo necessário para investigar estados inválidos.

    O alerta não inclui dados do paciente, telefone ou erro de entrega. O
    logging é best-effort para que um handler operacional mal configurado não
    impeça a reconstrução da planilha.
    """
    unknown_dispatches = [
        dispatch
        for dispatch in dispatches
        if _normalized_dispatch_status(dispatch) == UNKNOWN_DISPATCH_STATUS
    ]
    if not unknown_dispatches:
        return

    alert = {
        'unknown_dispatch_count': len(unknown_dispatches),
        'unknown_status_values': sorted({
            _unknown_status_value(dispatch)
            for dispatch in unknown_dispatches
        }),
        'unknown_dispatches': [
            {
                'dispatch_id': dispatch.id,
                'message_type': dispatch.message_type,
            }
            for dispatch in unknown_dispatches
        ],
    }
    try:
        logger.warning(
            'botox_sheet_unknown_dispatch_status',
            extra=alert,
        )
    except Exception:
        # A reconstrução da planilha é o caminho principal e não pode falhar
        # por causa de um sink de alertas indisponível.
        pass


def _aggregate_dispatches(dispatches):
    """Resume dispatches do mesmo tipo sem esconder uma execução problemática.

    A aba mantém uma linha por paciente/data, portanto uma linha pode
    representar vários dispatches. Tentativas e erros são dados acumulados de
    todas as execuções; o status é o estado mais acionável, com falha terminal
    sempre vencendo os demais estados.
    """
    if not dispatches:
        return None

    normalized = [
        (_normalized_dispatch_status(dispatch), dispatch)
        for dispatch in dispatches
    ]
    status, _dispatch = max(
        normalized,
        key=lambda item: _DISPATCH_STATUS_PRIORITY[item[0]],
    )
    attempts = sum(dispatch.attempts or 0 for dispatch in dispatches)
    errors = [
        f'execução {dispatch.execution_id}: {dispatch.last_error}'
        for dispatch in dispatches
        if dispatch.last_error
    ]
    errors.extend(
        f'execução {dispatch.execution_id}: estado desconhecido: '
        + (dispatch.status.strip() if isinstance(dispatch.status, str)
           and dispatch.status.strip() else '(vazio)')
        for normalized_status, dispatch in normalized
        if normalized_status == UNKNOWN_DISPATCH_STATUS
    )
    sent_at = max(
        (
            dispatch.sent_at
            for dispatch in dispatches
            if dispatch.sent_at
        ),
        default=None,
    )
    return {
        'status': status,
        'attempts': attempts,
        'last_error': '; '.join(errors),
        'sent_at': sent_at,
    }


def build_botox_sheet_rows():
    """Retorna a matriz de valores, agrupada por paciente e data."""
    from models import CosmeticProcedurePlan, Note, Patient, ProcedureExecution, db
    from services.google_sheets import BOTOX_HEADERS, format_phone_for_sheets

    rows = (
        db.session.query(ProcedureExecution, Patient)
        .join(
            CosmeticProcedurePlan,
            ProcedureExecution.plan_id == CosmeticProcedurePlan.id,
        )
        .join(Note, CosmeticProcedurePlan.note_id == Note.id)
        .join(Patient, Note.patient_id == Patient.id)
        .filter(
            ProcedureExecution.execution_status == 'realizada',
            ProcedureExecution.performed_date.isnot(None),
            db.func.lower(CosmeticProcedurePlan.procedure_name).like('%botox%'),
        )
        .order_by(
            ProcedureExecution.performed_date.asc(),
            ProcedureExecution.id.asc(),
        )
        .all()
    )

    groups = OrderedDict()
    for execution, patient in rows:
        key = (patient.id, execution.performed_date.date())
        group = groups.setdefault(key, {
            'patient': patient,
            'performed_date': execution.performed_date,
            'followup_date': execution.followup_date,
            'execution_ids': [],
        })
        group['execution_ids'].append(execution.id)
        if not group['followup_date'] and execution.followup_date:
            group['followup_date'] = execution.followup_date

    from models import MessageDispatch

    patient_ids = [group['patient'].id for group in groups.values()]
    dispatches = []
    if patient_ids:
        dispatches = db.session.query(MessageDispatch).filter(
            MessageDispatch.patient_id.in_(patient_ids)
        ).all()
    dispatches_by_key = defaultdict(list)
    for dispatch in dispatches:
        dispatches_by_key[
            (dispatch.execution_id, dispatch.message_type)
        ].append(dispatch)
    execution_ids = {
        execution_id
        for group in groups.values()
        for execution_id in group['execution_ids']
    }
    _alert_unknown_dispatches([
        dispatch
        for dispatch in dispatches
        if dispatch.execution_id in execution_ids
        and dispatch.message_type in BOTOX_MESSAGE_TYPES
    ])

    def _d(value):
        return value.strftime('%d/%m/%Y') if value else ''

    def _dt(value):
        return value.strftime('%d/%m/%Y %H:%M') if value else ''

    matrix = [list(BOTOX_HEADERS)]
    for group in groups.values():
        patient = group['patient']
        performed_date = group['performed_date']
        followup_date = group['followup_date']

        def _dispatches(message_type):
            return [
                dispatch
                for execution_id in group['execution_ids']
                for dispatch in dispatches_by_key.get(
                    (execution_id, message_type),
                    [],
                )
            ]

        def _status(dispatch):
            if not dispatch:
                return ''
            if dispatch['status'] == 'falhou':
                return 'falhou (terminal)'
            return dispatch['status']

        def _attempts(dispatch):
            return dispatch['attempts'] if dispatch else ''

        def _error(dispatch):
            return dispatch['last_error'] if dispatch else ''

        disp_d0 = _aggregate_dispatches(_dispatches('d0'))
        disp_m5 = _aggregate_dispatches(_dispatches('m5'))
        matrix.append([
            ', '.join(str(execution_id) for execution_id in group['execution_ids']),
            patient.name or '',
            format_phone_for_sheets(patient.phone),
            _d(performed_date),
            _d(followup_date),
            _status(disp_d0),
            _attempts(disp_d0),
            _error(disp_d0),
            _dt(disp_d0['sent_at']) if disp_d0 else '',
            _status(disp_m5),
            _attempts(disp_m5),
            _error(disp_m5),
            _dt(disp_m5['sent_at']) if disp_m5 else '',
        ])
    return matrix


def run_botox_sheet_sync():
    """Reconcilia a planilha, evitando concorrência entre workers."""
    from models import db
    from services.google_sheets import write_botox_sheet

    if db.engine.dialect.name != 'postgresql':
        return write_botox_sheet(build_botox_sheet_rows())

    with db.engine.connect() as connection:
        acquired = connection.execute(
            text('SELECT pg_try_advisory_lock(:key)'),
            {'key': ADVISORY_LOCK_KEY},
        ).scalar()
        if not acquired:
            return True, 'ignorado: outro worker já está sincronizando'

        try:
            return write_botox_sheet(build_botox_sheet_rows())
        finally:
            connection.execute(
                text('SELECT pg_advisory_unlock(:key)'),
                {'key': ADVISORY_LOCK_KEY},
            )