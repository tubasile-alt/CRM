"""Fundação de dados para mensagens D0 e M5 de procedimentos de Botox."""

import os
from types import SimpleNamespace

from dateutil.relativedelta import relativedelta
from sqlalchemy import event, inspect, select, text

from models import CosmeticProcedurePlan, MessageDispatch, ProcedureExecution
from services.clinic_time import clinic_today


FOLLOWUP_MONTHS_BOTOX = 5
DISPATCH_ENABLED = os.environ.get('MESSAGE_DISPATCH_ENABLED') == '1'


def is_botox(procedure_name: str) -> bool:
    return 'botox' in (procedure_name or '').lower()


def compute_m5_date(performed_date):
    return (
        performed_date + relativedelta(months=FOLLOWUP_MONTHS_BOTOX)
    ).date()


def build_dispatch_rows(execution, plan, today=None):
    """Monta dispatches D0 e M5 sem escrever no banco."""
    if (
        execution.execution_status != 'realizada'
        or not execution.performed_date
        or not is_botox(plan.procedure_name)
    ):
        return []

    today = today or clinic_today()
    performed_date = execution.performed_date.date()
    d0_status = 'pendente' if performed_date >= today else 'pulada'

    return [
        {
            'execution_id': execution.id,
            'message_type': 'd0',
            'due_at': performed_date,
            'status': d0_status,
        },
        {
            'execution_id': execution.id,
            'message_type': 'm5',
            'due_at': compute_m5_date(execution.performed_date),
            'status': 'pendente',
        },
    ]


@event.listens_for(ProcedureExecution, 'before_insert')
@event.listens_for(ProcedureExecution, 'before_update')
def _set_followup_date(mapper, connection, target):
    del mapper
    if not DISPATCH_ENABLED:
        return
    if (
        target.execution_status == 'realizada'
        and target.performed_date
        and not target.followup_date
        and is_botox(_procedure_name_for_target(connection, target))
    ):
        target.followup_date = target.performed_date + relativedelta(
            months=FOLLOWUP_MONTHS_BOTOX
        )


def _procedure_name_for_target(connection, target):
    plan = target.__dict__.get('plan')
    if plan is not None:
        return plan.procedure_name
    return connection.execute(
        select(CosmeticProcedurePlan.procedure_name).where(
            CosmeticProcedurePlan.id == target.plan_id
        )
    ).scalar_one_or_none()


def _load_plan(connection, target):
    plan = target.__dict__.get('plan')
    if plan is not None:
        return plan
    procedure_name = _procedure_name_for_target(connection, target)
    if procedure_name is None:
        return None
    return SimpleNamespace(procedure_name=procedure_name)


def _resolve_patient_id(connection, execution):
    row = connection.execute(text("""
        SELECT n.patient_id
          FROM cosmetic_procedure_plan p
          JOIN note n ON n.id = p.note_id
         WHERE p.id = :plan_id
    """), {'plan_id': execution.plan_id}).first()
    return row[0] if row else None


def _dispatch_exists(connection, patient_id, message_type, due_at):
    return connection.execute(text("""
        SELECT 1
          FROM message_dispatch
         WHERE patient_id = :patient_id
           AND message_type = :message_type
           AND due_at = :due_at
    """), {
        'patient_id': patient_id,
        'message_type': message_type,
        'due_at': due_at,
    }).first() is not None


def _insert_missing_dispatches(connection, target):
    plan = _load_plan(connection, target)
    if plan is None:
        return

    patient_id = _resolve_patient_id(connection, target)
    if patient_id is None:
        return

    rows = build_dispatch_rows(target, plan)
    if not rows:
        return

    missing_rows = []
    for row in rows:
        if _dispatch_exists(
            connection,
            patient_id,
            row['message_type'],
            row['due_at'],
        ):
            continue
        row = dict(row)
        row['patient_id'] = patient_id
        missing_rows.append(row)
    if missing_rows:
        connection.execute(MessageDispatch.__table__.insert(), missing_rows)


@event.listens_for(ProcedureExecution, 'after_insert')
def _sync_dispatches_after_insert(mapper, connection, target):
    del mapper
    if not DISPATCH_ENABLED:
        return
    _insert_missing_dispatches(connection, target)


@event.listens_for(ProcedureExecution, 'after_update')
def _sync_dispatches_after_update(mapper, connection, target):
    del mapper
    if not DISPATCH_ENABLED:
        return
    history = inspect(target).attrs.execution_status.history
    transitioned_to_realized = (
        history.has_changes()
        and target.execution_status == 'realizada'
        and 'realizada' in history.added
    )
    if transitioned_to_realized:
        _insert_missing_dispatches(connection, target)


def register_followup_listeners():
    """Marca o import explícito que registra os listeners deste módulo."""
    return None