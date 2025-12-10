from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from models import db, Patient, CosmeticProcedurePlan, Note, User
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
import pytz

crm_bp = Blueprint('crm', __name__)

@crm_bp.route('/crm')
@login_required
def crm_page():
    return render_template('crm.html')

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
        
        result.append({
            'id': plan.id,
            'patient_id': patient.id,
            'patient_name': patient.name,
            'procedure_name': plan.procedure_name,
            'performed_date': plan.performed_date.isoformat() if plan.performed_date else None,
            'follow_up_due_at': follow_up_due_at.isoformat() if follow_up_due_at else None,
            'follow_up_months': plan.follow_up_months or 6,
            'observations': plan.observations
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
        
        result.append({
            'id': plan.id,
            'patient_id': patient.id,
            'patient_name': patient.name,
            'patient_phone': patient.phone,
            'procedure_name': plan.procedure_name,
            'performed_date': plan.performed_date.isoformat() if plan.performed_date else None,
            'follow_up_due_at': follow_up_due_at.isoformat(),
            'days_until': days_until,
            'urgency': status_label
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
        result.append({
            'id': plan.id,
            'patient_id': patient.id,
            'patient_name': patient.name,
            'patient_phone': patient.phone,
            'procedure_name': plan.procedure_name,
            'planned_value': float(plan.planned_value) if plan.planned_value else None,
            'observations': plan.observations,
            'created_at': plan.created_at.isoformat() if plan.created_at else None
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
