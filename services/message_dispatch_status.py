"""Contrato único dos estados de um dispatch de mensagem.

O fluxo de dispatch cria registros como ``pendente`` ou ``pulada``, pode
reservá-los como ``reservada`` e recebe do integrador um resultado terminal:
``enviada``, ``falhou`` ou ``cancelada``. A reconciliação da aba Botox aceita
todos esses estados conhecidos. Valores fora deste contrato são dados
inesperados e devem ser exibidos como ``desconhecido``, nunca como um estado
arbitrário da planilha.
"""

DISPATCH_PENDING_STATUS = 'pendente'
DISPATCH_SKIPPED_STATUS = 'pulada'
DISPATCH_CREATED_STATUSES = frozenset({
    DISPATCH_PENDING_STATUS,
    DISPATCH_SKIPPED_STATUS,
})
DISPATCH_RESERVED_STATUS = 'reservada'
DISPATCH_RESULT_STATUSES = frozenset({'enviada', 'falhou', 'cancelada'})
DISPATCH_KNOWN_STATUSES = frozenset({
    *DISPATCH_CREATED_STATUSES,
    DISPATCH_RESERVED_STATUS,
    *DISPATCH_RESULT_STATUSES,
})
DISPATCH_ACTIVE_STATUSES = frozenset({
    DISPATCH_PENDING_STATUS,
    DISPATCH_RESERVED_STATUS,
})
UNKNOWN_DISPATCH_STATUS = 'desconhecido'


def normalize_dispatch_status(value):
    """Converte qualquer valor fora do contrato em um estado seguro."""
    status = value.strip() if isinstance(value, str) else ''
    return status if status in DISPATCH_KNOWN_STATUSES else UNKNOWN_DISPATCH_STATUS


def unknown_dispatch_status_value(value):
    """Retorna o valor original de um estado inválido para investigação."""
    status = value.strip() if isinstance(value, str) else ''
    return status or '(vazio)'


class DispatchStatusCorrectionError(ValueError):
    """Erro de validação de uma correção manual de dispatch."""


def _unknown_dispatch_filter(model):
    """Cria o filtro SQL que também inclui status nulo e espaços em branco."""
    from sqlalchemy import func, or_

    return or_(
        model.status.is_(None),
        func.trim(model.status).notin_(DISPATCH_KNOWN_STATUSES),
    )


def _serialize_dispatch_review(dispatch, patient, execution, plan):
    def _iso(value):
        return value.isoformat() if value else None

    return {
        'dispatch_id': dispatch.id,
        'status': dispatch.status,
        'normalized_status': normalize_dispatch_status(dispatch.status),
        'patient_id': dispatch.patient_id,
        'patient_name': getattr(patient, 'name', None),
        'execution_id': dispatch.execution_id,
        'execution_status': getattr(execution, 'execution_status', None),
        'procedure_name': getattr(plan, 'procedure_name', None),
        'message_type': dispatch.message_type,
        'due_at': _iso(dispatch.due_at),
        'performed_at': _iso(getattr(execution, 'performed_date', None)),
        'attempts': dispatch.attempts or 0,
        'reserved_at': _iso(dispatch.reserved_at),
        'sent_at': _iso(dispatch.sent_at),
        'last_error': dispatch.last_error,
        'created_at': _iso(dispatch.created_at),
    }


def list_unknown_dispatches(limit=50, offset=0):
    """Lista estados inválidos sem modificar qualquer registro."""
    from models import (
        CosmeticProcedurePlan,
        MessageDispatch,
        Patient,
        ProcedureExecution,
        db,
    )

    try:
        limit = min(max(1, int(limit)), 100)
        offset = max(0, int(offset))
    except (TypeError, ValueError):
        raise DispatchStatusCorrectionError(
            'limit e offset devem ser números inteiros válidos'
        )

    filter_ = _unknown_dispatch_filter(MessageDispatch)
    total = db.session.query(MessageDispatch.id).filter(filter_).count()
    rows = (
        db.session.query(
            MessageDispatch,
            Patient,
            ProcedureExecution,
            CosmeticProcedurePlan,
        )
        .outerjoin(Patient, Patient.id == MessageDispatch.patient_id)
        .outerjoin(
            ProcedureExecution,
            ProcedureExecution.id == MessageDispatch.execution_id,
        )
        .outerjoin(
            CosmeticProcedurePlan,
            CosmeticProcedurePlan.id == ProcedureExecution.plan_id,
        )
        .filter(filter_)
        .order_by(MessageDispatch.id.asc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return {
        'total': total,
        'limit': limit,
        'offset': offset,
        'dispatches': [
            _serialize_dispatch_review(dispatch, patient, execution, plan)
            for dispatch, patient, execution, plan in rows
        ],
    }


def correct_unknown_dispatch(
    dispatch_id,
    target_status,
    actor='integration_api',
    reason=None,
    expected_status=None,
):
    """Corrige um único estado inválido e registra a transição.

    A operação só altera um dispatch ainda desconhecido. Se outra operação já
    o corrigiu, a resposta é idempotente e nenhum novo log é criado.
    """
    from models import MessageDispatch, MessageDispatchStatusAudit, db

    target_status = (
        target_status.strip()
        if isinstance(target_status, str)
        else ''
    )
    if target_status not in DISPATCH_KNOWN_STATUSES:
        raise DispatchStatusCorrectionError(
            'target_status deve ser um estado aceito: '
            + ', '.join(sorted(DISPATCH_KNOWN_STATUSES))
        )

    actor = (str(actor or '').strip() or 'integration_api')[:100]
    reason = (str(reason).strip() if reason is not None else '')[:500] or None

    dispatch = (
        db.session.query(MessageDispatch)
        .filter(MessageDispatch.id == dispatch_id)
        .with_for_update()
        .one_or_none()
    )
    if dispatch is None:
        return None

    current_status = dispatch.status
    if normalize_dispatch_status(current_status) != UNKNOWN_DISPATCH_STATUS:
        return {
            'dispatch': dispatch,
            'audit': None,
            'changed': False,
            'previous_status': current_status,
        }

    if expected_status is not None and current_status != expected_status:
        raise DispatchStatusCorrectionError(
            'o estado atual não corresponde ao estado revisado'
        )

    dispatch.status = target_status
    audit = MessageDispatchStatusAudit(
        dispatch_id=dispatch.id,
        previous_status=current_status,
        new_status=target_status,
        actor=actor,
        reason=reason,
    )
    db.session.add(audit)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    return {
        'dispatch': dispatch,
        'audit': audit,
        'changed': True,
        'previous_status': current_status,
    }