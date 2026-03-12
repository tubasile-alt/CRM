import json
from datetime import timedelta
from decimal import Decimal

from models import CommercialTask, Patient, User, db, get_brazil_time

DERMA_SOURCE_TYPE = 'derma'
CP_SOURCE_TYPE = 'cp'
VALID_STATUSES = {'novo', 'conversado', 'aguardando', 'fechado', 'perdido'}
VALID_PRIORITIES = {'alta', 'media', 'baixa'}

# Escopo atual do dashboard comercial DERMA (expansível no futuro sem quebrar CP)
DERMA_DASHBOARD_DOCTOR_USERNAMES = {'tubasile'}  # Dr. Arthur
CP_DOCTOR_USERNAMES = {'fibasile', 'vinibasile', 'rbasile'}  # Dr. Filipe, Dr. Vinicius, Dr. Basile


def _to_float(value):
    if value is None:
        return 0.0
    if isinstance(value, (int, float, Decimal)):
        return float(value)
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def detect_medical_record_source(category, doctor=None, appointment=None):
    """Identifica explicitamente a origem do prontuário para isolar DERMA/CP."""
    if category == 'transplante_capilar':
        return CP_SOURCE_TYPE

    doctor_role = (getattr(doctor, 'role_clinico', '') or '').upper()
    if doctor_role == 'CP':
        return CP_SOURCE_TYPE

    appointment_type = (getattr(appointment, 'appointment_type', '') or '').strip().lower()
    if appointment_type in {'transplante capilar', 'transplante_capilar'}:
        return CP_SOURCE_TYPE

    return DERMA_SOURCE_TYPE


def is_derma_consultation(category, doctor=None, appointment=None):
    return detect_medical_record_source(category, doctor=doctor, appointment=appointment) == DERMA_SOURCE_TYPE


def is_commercial_derma_doctor(doctor):
    if not doctor:
        return False
    username = (doctor.username or '').strip().lower()
    return username in DERMA_DASHBOARD_DOCTOR_USERNAMES


def get_derma_dashboard_doctors():
    return User.query.filter(
        User.role == 'medico',
        User.username.in_(list(DERMA_DASHBOARD_DOCTOR_USERNAMES))
    ).order_by(User.name.asc()).all()


def get_commercial_filter_doctors():
    """Lista todos os médicos para o filtro visual do comercial."""
    return User.query.filter(
        User.role == 'medico',
    ).order_by(User.name.asc()).all()


def get_cp_doctors():
    return User.query.filter(
        User.role == 'medico',
        User.username.in_(list(CP_DOCTOR_USERNAMES))
    ).order_by(User.name.asc()).all()


def extract_derma_planning_snapshot(cosmetic_procedures_data):
    if not cosmetic_procedures_data:
        return None

    planned_items = []
    for proc in cosmetic_procedures_data:
        name = (proc.get('name') or '').strip()
        planned_value = _to_float(proc.get('value'))
        budget_value = _to_float(proc.get('budget', planned_value))
        performed = bool(proc.get('performed', False))

        # Evita tarefas vazias (ex.: linha em branco no front)
        has_meaningful_payload = bool(name) or planned_value > 0 or budget_value > 0 or performed
        if not has_meaningful_payload:
            continue

        planned_items.append({
            'name': name or 'Procedimento',
            'planned_value': planned_value,
            'budget_value': budget_value,
            'performed': performed,
            'performed_date': proc.get('performedDate') or proc.get('performed_date') or None,
            'follow_up_months': int(proc.get('months') or proc.get('follow_up_months') or 0),
            'observations': proc.get('observations', ''),
        })

    if not planned_items:
        return None

    return {
        'items': planned_items,
        'generated_at': get_brazil_time().isoformat(),
    }


def upsert_task_from_consultation(patient_id, doctor_id, consultation_id, planning_snapshot, consultation_dt=None):
    if not planning_snapshot:
        return None

    patient = db.session.get(Patient, patient_id)
    doctor = db.session.get(User, doctor_id)
    if not patient or not doctor or not is_commercial_derma_doctor(doctor):
        return None

    total_value = sum(_to_float(item.get('budget_value')) for item in planning_snapshot.get('items', []))

    task = CommercialTask.query.filter_by(
        consultation_id=consultation_id,
        source_type=DERMA_SOURCE_TYPE,
    ).first()

    if task is None:
        task = CommercialTask(
            patient_id=patient_id,
            doctor_id=doctor_id,
            consultation_id=consultation_id,
            source_type=DERMA_SOURCE_TYPE,
            status='novo',
            priority='media',
        )

    task.patient_name_snapshot = patient.name
    task.doctor_name_snapshot = doctor.name
    task.planning_snapshot_json = json.dumps(planning_snapshot, ensure_ascii=False)
    task.total_value = total_value
    task.consultation_date = consultation_dt or task.consultation_date

    if task.status == 'fechado':
        task.status = 'aguardando'

    db.session.add(task)
    return task


def build_whatsapp_message(task, template='pos_consulta'):
    items = [f"- {item.get('name')} (R$ {item.get('budget_value', 0):,.2f})" for item in task.snapshot_items]
    procedures_text = '\n'.join(items) if items else '- Procedimentos planejados em avaliação'
    total = f"R$ {task.total_value_float:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

    if template == 'orcamento':
        intro = f"Olá, {task.patient_name_snapshot}! Segue seu orçamento da consulta com {task.doctor_name_snapshot}."
    elif template == 'follow_up':
        intro = f"Olá, {task.patient_name_snapshot}! Passando para acompanhar sua decisão sobre o planejamento com {task.doctor_name_snapshot}."
    elif template == 'retomada':
        intro = f"Oi, {task.patient_name_snapshot}! Podemos retomar o seu plano de tratamento com {task.doctor_name_snapshot}?"
    else:
        intro = f"Olá, {task.patient_name_snapshot}! Obrigada pela consulta com {task.doctor_name_snapshot}."

    return (
        f"{intro}\n\nProcedimentos planejados:\n{procedures_text}\n\n"
        f"Valor total estimado: {total}\n\nFico à disposição para te ajudar."
    )


def monday_and_sunday(reference=None):
    ref = reference or get_brazil_time().date()
    start = ref - timedelta(days=ref.weekday())
    end = start + timedelta(days=6)
    return start, end


def can_access_commercial(user):
    role = (getattr(user, 'role', '') or '').lower()
    role_clinico = (getattr(user, 'role_clinico', '') or '').upper()
    return role in {'secretaria', 'medico'} or role_clinico in {'SECRETARY', 'ADMIN'}
