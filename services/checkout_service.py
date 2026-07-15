from models import Payment, db
from services.clinic_time import get_brazil_time
from services.pricing import CONSULTATION_PRICES


def can_use_checkout(user):
    role = (getattr(user, 'role', '') or '').strip().lower()
    role_clinico = (getattr(user, 'role_clinico', '') or '').strip().upper()
    return role in {'secretaria', 'medico'} or role_clinico in {'SECRETARY', 'ADMIN'}


def can_manage_checkout_payment(user):
    role = (getattr(user, 'role', '') or '').strip().lower()
    role_clinico = (getattr(user, 'role_clinico', '') or '').strip().upper()
    return role == 'secretaria' or role_clinico in {'SECRETARY', 'ADMIN'}


def _procedure_has_execution(procedure, execution_id):
    return str(procedure.get('execution_id') or '') == str(execution_id)


def _payment_contains_execution(payment, execution_id):
    return any(_procedure_has_execution(item, execution_id) for item in (payment.procedures or []))


def _consultation_item(consultation_type):
    consultation_fee = CONSULTATION_PRICES.get(consultation_type, 0.0)
    if consultation_fee <= 0:
        return None
    return {
        'name': f'Consulta {consultation_type}',
        'value': float(consultation_fee),
        'source': 'consultation',
    }


def _execution_item(plan, execution):
    return {
        'name': plan.procedure_name or plan.name or 'Procedimento',
        'value': float(execution.charged_value or plan.final_budget or plan.planned_value or 0),
        'source': 'procedure_execution',
        'plan_id': plan.id,
        'execution_id': execution.id,
    }


def _recalculate_total(payment):
    payment.total_amount = sum(float(item.get('value', 0) or 0) for item in (payment.procedures or []))


def _find_existing_payment_for_execution(patient_id, execution_id):
    payments = Payment.query.filter_by(patient_id=patient_id).all()
    for payment in payments:
        if _payment_contains_execution(payment, execution_id):
            return payment
    return None


def _find_pending_payment(patient_id, appointment_id):
    query = Payment.query.filter_by(patient_id=patient_id, status='pendente')
    if appointment_id:
        return query.filter_by(appointment_id=appointment_id).order_by(Payment.created_at.desc()).first()
    return None


def ensure_checkout_for_execution(plan, execution):
    status = (execution.execution_status or ('realizada' if execution.was_performed else 'agendada')).lower()
    if status != 'realizada':
        return None

    note = plan.note
    if not note:
        return None

    patient_id = note.patient_id
    appointment_id = note.appointment_id
    existing = _find_existing_payment_for_execution(patient_id, execution.id)
    if existing:
        return existing

    procedure_item = _execution_item(plan, execution)
    payment = _find_pending_payment(patient_id, appointment_id)

    if payment:
        procedures = list(payment.procedures or [])
        if not any(_procedure_has_execution(item, execution.id) for item in procedures):
            procedures.append(procedure_item)
            payment.procedures = procedures
            _recalculate_total(payment)
        return payment

    consultation_type = 'Particular'
    if note.appointment and note.appointment.appointment_type:
        consultation_type = note.appointment.appointment_type

    procedures = []
    consultation = _consultation_item(consultation_type)
    if consultation:
        procedures.append(consultation)
    procedures.append(procedure_item)
    total_amount = sum(float(item.get('value', 0) or 0) for item in procedures)
    if total_amount <= 0:
        return None

    payment = Payment(
        appointment_id=appointment_id,
        patient_id=patient_id,
        total_amount=total_amount,
        consultation_type=consultation_type,
        payment_method='pendente',
        status='pendente',
        procedures=procedures,
        created_at=get_brazil_time(),
    )
    db.session.add(payment)
    return payment
