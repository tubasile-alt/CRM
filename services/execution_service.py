"""Shared helpers extracted from app.py without behavior changes."""

from datetime import datetime
from flask import request
from flask_login import current_user
from models import ProcedureExecution


def _parse_date_or_datetime(value):
    if not value:
        return None
    if isinstance(value, datetime):
        return value
    try:
        value_str = str(value).strip()
        if len(value_str) == 10:
            return datetime.strptime(value_str, '%Y-%m-%d')
        return datetime.fromisoformat(value_str.replace('Z', ''))
    except Exception:
        return None

def _serialize_execution(execution):
    execution_status = (execution.execution_status or ('realizada' if execution.was_performed else 'agendada')).lower()
    return {
        'id': execution.id,
        'plan_id': execution.plan_id,
        'scheduled_date': execution.scheduled_date.isoformat() if execution.scheduled_date else None,
        'performed_date': execution.performed_date.isoformat() if execution.performed_date else None,
        'execution_status': execution_status,
        'was_performed': execution_status == 'realizada',
        'charged_value': float(execution.charged_value) if execution.charged_value is not None else None,
        'notes': execution.notes,
        'followup_date': execution.followup_date.isoformat() if execution.followup_date else None,
        'followup_status': execution.followup_status,
        'created_at': execution.created_at.isoformat() if execution.created_at else None,
    }

def _build_execution_from_payload(plan, data, force_performed=False):
    allowed_statuses = {'agendada', 'realizada', 'cancelada', 'faltou'}
    allowed_followup = {'pendente', 'contatado', 'agendado', 'sem_resposta'}

    scheduled_date = _parse_date_or_datetime(data.get('scheduled_date'))
    performed_date = _parse_date_or_datetime(data.get('performed_date'))

    if force_performed:
        execution_status = 'realizada'
    else:
        raw_status = (data.get('execution_status') or '').strip().lower()
        if raw_status in allowed_statuses:
            execution_status = raw_status
        else:
            execution_status = 'realizada' if bool(data.get('was_performed', bool(performed_date))) else 'agendada'

    if execution_status == 'realizada' and not performed_date:
        raise ValueError('performed_date é obrigatório quando execution_status=realizada')
    if execution_status == 'agendada' and not scheduled_date:
        raise ValueError('scheduled_date é obrigatório quando execution_status=agendada')

    was_performed = execution_status == 'realizada'

    charged_raw = data.get('charged_value', data.get('planned_value', plan.final_budget or plan.planned_value))
    charged_value = None
    if charged_raw not in (None, ''):
        try:
            charged_value = float(charged_raw)
        except (TypeError, ValueError):
            raise ValueError('charged_value inválido')
        if charged_value < 0:
            raise ValueError('charged_value não pode ser negativo')

    followup_date = _parse_date_or_datetime(data.get('followup_date'))
    followup_status = (data.get('followup_status') or 'pendente').strip().lower()
    if followup_status not in allowed_followup:
        raise ValueError('followup_status inválido')

    return ProcedureExecution(
        plan_id=plan.id,
        scheduled_date=scheduled_date,
        performed_date=performed_date,
        execution_status=execution_status,
        was_performed=was_performed,
        charged_value=charged_value,
        notes=data.get('notes') or data.get('observations'),
        followup_date=followup_date,
        followup_status=followup_status,
        created_by=current_user.id,
        updated_by=current_user.id,
        idempotency_key=(data.get('idempotency_key') or request.headers.get('X-Idempotency-Key') or '').strip() or None,
    )
