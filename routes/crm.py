from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from models import db, Patient, CosmeticProcedurePlan, Note, User, Appointment, TransplantSurgeryRecord, PatientDoctor
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from sqlalchemy import func, extract
import pytz


def _get_dp_id(patient_id, doctor_id):
    if not doctor_id:
        return None
    dp = PatientDoctor.query.filter_by(patient_id=patient_id, doctor_id=doctor_id).first()
    return dp.id if dp else None

crm_bp = Blueprint('crm', __name__)

@crm_bp.route('/crm')
@login_required
def crm_page():
    is_marcella = (current_user.username or '').strip().lower() == 'marcella'
    return render_template('crm.html', is_marcella=is_marcella)

@crm_bp.route('/api/crm/transplant-stats')
@login_required
def get_transplant_stats():
    # Atendimentos de transplante por mês (últimos 12 meses)
    today = date.today()
    start_date = today - relativedelta(months=11)
    start_date = start_date.replace(day=1)
    
    stats = db.session.query(
        extract('year', Appointment.start_time).label('year'),
        extract('month', Appointment.start_time).label('month'),
        func.count(Appointment.id).label('count')
    ).filter(
        Appointment.appointment_type == 'Transplante Capilar',
        Appointment.start_time >= start_date
    ).group_by('year', 'month').order_by('year', 'month').all()
    
    result = []
    for s in stats:
        result.append({
            'month': f"{int(s.month):02d}/{int(s.year)}",
            'count': s.count
        })
    
    return jsonify(result)

@crm_bp.route('/api/crm/pending-surgeries')
@login_required
def get_pending_surgeries():
    # Pacientes que tem planejamento cirúrgico mas não tem registro de cirurgia
    from models import HairTransplant, Note
    
    # Subconsulta: pacientes que JÁ POSSUEM registro de cirurgia
    subquery = db.session.query(TransplantSurgeryRecord.patient_id).distinct()
    
    # Busca pacientes que possuem a nota de planejamento preenchida
    # mas não estão na subconsulta de cirurgias já agendadas/realizadas
    patients = db.session.query(Patient).join(
        Note, Patient.id == Note.patient_id
    ).join(
        HairTransplant, Note.id == HairTransplant.note_id
    ).filter(
        HairTransplant.surgical_planning != None,
        HairTransplant.surgical_planning != '',
        ~Patient.id.in_(subquery)
    ).distinct().all()
    
    result = []
    for p in patients:
        last_app = db.session.query(Appointment).filter_by(
            patient_id=p.id,
            appointment_type='Transplante Capilar'
        ).order_by(Appointment.start_time.desc()).first()
        doctor_id = last_app.doctor_id if last_app else None
        dp_id = _get_dp_id(p.id, doctor_id)
        result.append({
            'id': p.id,
            'name': p.name,
            'phone': p.phone,
            'last_consultation': last_app.start_time.strftime('%d/%m/%Y') if last_app else 'N/A',
            'dp_id': dp_id
        })
    
    return jsonify(result)

@crm_bp.route('/api/crm/performed')
@login_required
def get_performed_procedures():
    # Pega procedimentos realizados do planejamento de cosmiatria
    query = db.session.query(CosmeticProcedurePlan, Note, Patient).join(
        Note, CosmeticProcedurePlan.note_id == Note.id
    ).join(
        Patient, Note.patient_id == Patient.id
    ).filter(CosmeticProcedurePlan.was_performed == True)
    
    if current_user.is_doctor():
        query = query.filter(Note.doctor_id == current_user.id)
    
    plans = query.order_by(CosmeticProcedurePlan.performed_date.desc()).limit(100).all()
    
    result = []
    for plan, note, patient in plans:
        follow_up_due_at = None
        if plan.performed_date and plan.follow_up_months:
            follow_up_due_at = (plan.performed_date + relativedelta(months=plan.follow_up_months)).date()
        dp_id = _get_dp_id(patient.id, note.doctor_id)
        result.append({
            'id': plan.id,
            'patient_id': patient.id,
            'patient_name': patient.name,
            'procedure_name': plan.procedure_name,
            'performed_date': plan.performed_date.isoformat() if plan.performed_date else None,
            'follow_up_due_at': follow_up_due_at.isoformat() if follow_up_due_at else None,
            'follow_up_months': plan.follow_up_months or 6,
            'observations': plan.observations,
            'dp_id': dp_id
        })
    
    return jsonify(result)

@crm_bp.route('/api/crm/followups')
@login_required
def get_followups():
    today = date.today()
    
    # Pega procedimentos realizados que precisam de follow-up
    query = db.session.query(CosmeticProcedurePlan, Note, Patient).join(
        Note, CosmeticProcedurePlan.note_id == Note.id
    ).join(
        Patient, Note.patient_id == Patient.id
    ).filter(CosmeticProcedurePlan.was_performed == True)
    
    if current_user.is_doctor():
        query = query.filter(Note.doctor_id == current_user.id)
    
    plans = query.all()
    
    result = []
    for plan, note, patient in plans:
        if not plan.performed_date or not plan.follow_up_months:
            continue
        
        follow_up_due_at = (plan.performed_date + relativedelta(months=plan.follow_up_months)).date()
        days_until = (follow_up_due_at - today).days
        
        status_label = 'Vencido' if days_until < 0 else ('Próximo' if days_until <= 30 else 'Futuro')
        
        dp_id = _get_dp_id(patient.id, note.doctor_id)
        result.append({
            'id': plan.id,
            'patient_id': patient.id,
            'patient_name': patient.name,
            'patient_phone': patient.phone,
            'procedure_name': plan.procedure_name,
            'performed_date': plan.performed_date.isoformat() if plan.performed_date else None,
            'follow_up_due_at': follow_up_due_at.isoformat(),
            'days_until': days_until,
            'urgency': status_label,
            'dp_id': dp_id
        })
    
    result.sort(key=lambda x: x['follow_up_due_at'])
    return jsonify(result[:100])

@crm_bp.route('/api/crm/planned')
@login_required
def get_planned_procedures():
    # Pega procedimentos planejados mas NÃO realizados
    query = db.session.query(CosmeticProcedurePlan, Note, Patient).join(
        Note, CosmeticProcedurePlan.note_id == Note.id
    ).join(
        Patient, Note.patient_id == Patient.id
    ).filter(CosmeticProcedurePlan.was_performed == False)
    
    if current_user.is_doctor():
        query = query.filter(Note.doctor_id == current_user.id)
    
    plans = query.order_by(CosmeticProcedurePlan.created_at.desc()).limit(100).all()
    
    result = []
    for plan, note, patient in plans:
        dp_id = _get_dp_id(patient.id, note.doctor_id)
        result.append({
            'id': plan.id,
            'patient_id': patient.id,
            'patient_name': patient.name,
            'patient_phone': patient.phone,
            'procedure_name': plan.procedure_name,
            'planned_value': float(plan.planned_value) if plan.planned_value else None,
            'observations': plan.observations,
            'created_at': plan.created_at.isoformat() if plan.created_at else None,
            'dp_id': dp_id
        })
    
    return jsonify(result)


@crm_bp.route('/api/crm/marcella-sales-funnel')
@login_required
def get_marcella_sales_funnel():
    """Retorna pendências de procedimentos do Dr. Arthur Basile para a usuária Marcella."""
    if (current_user.username or '').strip().lower() != 'marcella':
        return jsonify({'error': 'Acesso restrito'}), 403

    arthur_doctor = User.query.filter(
        db.func.lower(User.name).like('%arthur%'),
        User.role == 'medico'
    ).first()

    if not arthur_doctor:
        return jsonify([])

    plans = db.session.query(CosmeticProcedurePlan, Note, Patient).join(
        Note, CosmeticProcedurePlan.note_id == Note.id
    ).join(
        Patient, Note.patient_id == Patient.id
    ).filter(
        CosmeticProcedurePlan.was_performed == False,
        Note.doctor_id == arthur_doctor.id
    ).order_by(
        Patient.name.asc(),
        CosmeticProcedurePlan.created_at.asc()
    ).all()

    result = []
    for plan, note, patient in plans:
        planned_date = plan.created_at.date().isoformat() if plan.created_at else None
        result.append({
            'plan_id': plan.id,
            'patient_id': patient.id,
            'patient_name': patient.name,
            'procedure_name': plan.procedure_name,
            'planned_date': planned_date,
            'dp_id': _get_dp_id(patient.id, note.doctor_id)
        })

    return jsonify(result)

@crm_bp.route('/api/crm/records/<int:plan_id>', methods=['PATCH'])
@login_required
def update_cosmetic_plan(plan_id):
    plan = CosmeticProcedurePlan.query.get_or_404(plan_id)
    data = request.get_json()
    
    if 'was_performed' in data:
        plan.was_performed = data['was_performed']
        if data['was_performed'] and not plan.performed_date:
            plan.performed_date = datetime.now()
    
    if 'observations' in data:
        plan.observations = data['observations']
    
    db.session.commit()
    return jsonify({'success': True})

@crm_bp.route('/api/crm/stats')
@login_required
def get_crm_stats():
    today = date.today()
    
    # Conta procedimentos realizados e planejados
    query = db.session.query(CosmeticProcedurePlan, Note).join(
        Note, CosmeticProcedurePlan.note_id == Note.id
    )
    
    if current_user.is_doctor():
        query = query.filter(Note.doctor_id == current_user.id)
    
    plans = query.all()
    
    performed_count = sum(1 for plan, note in plans if plan.was_performed)
    planned_count = sum(1 for plan, note in plans if not plan.was_performed)
    
    overdue_count = 0
    due_soon_count = 0
    
    for plan, note in plans:
        if plan.was_performed and plan.performed_date and plan.follow_up_months:
            follow_up_due = (plan.performed_date + relativedelta(months=plan.follow_up_months)).date()
            days_until = (follow_up_due - today).days
            
            if days_until < 0:
                overdue_count += 1
            elif days_until <= 30:
                due_soon_count += 1
    
    return jsonify({
        'performed': performed_count,
        'planned': planned_count,
        'overdue': overdue_count,
        'due_soon': due_soon_count
    })
