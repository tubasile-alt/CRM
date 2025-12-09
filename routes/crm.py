from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from models import db, Patient, ProcedureRecord, ProcedureFollowUpRule, Evolution, User
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
import pytz

crm_bp = Blueprint('crm', __name__)

FOLLOW_UP_DEFAULTS = {
    'Botox': 6,
    'Preenchimento': 12,
    'Laser': 3,
    'Ulthera': 12,
    'Infiltração Capilar': 1,
    'Soroterapia': 1,
    'Nitrogênio Líquido': 1,
    'Retorno Botox': 6,
}

def get_follow_up_months(procedure_name):
    rule = ProcedureFollowUpRule.query.filter_by(procedure_name=procedure_name).first()
    if rule:
        return rule.follow_up_months
    return FOLLOW_UP_DEFAULTS.get(procedure_name, 6)

@crm_bp.route('/crm')
@login_required
def crm_page():
    return render_template('crm.html')

@crm_bp.route('/api/crm/performed')
@login_required
def get_performed_procedures():
    doctor_id = request.args.get('doctor_id', type=int)
    
    query = ProcedureRecord.query.filter_by(status='realizado')
    if doctor_id:
        query = query.filter_by(doctor_id=doctor_id)
    elif current_user.is_doctor():
        query = query.filter_by(doctor_id=current_user.id)
    
    records = query.order_by(ProcedureRecord.performed_date.desc()).limit(100).all()
    
    result = []
    for r in records:
        result.append({
            'id': r.id,
            'patient_id': r.patient_id,
            'patient_name': r.patient.name,
            'procedure_name': r.procedure_name,
            'performed_date': r.performed_date.isoformat() if r.performed_date else None,
            'follow_up_due_at': r.follow_up_due_at.isoformat() if r.follow_up_due_at else None,
            'follow_up_status': r.follow_up_status,
            'notes': r.notes
        })
    
    return jsonify(result)

@crm_bp.route('/api/crm/followups')
@login_required
def get_followups():
    doctor_id = request.args.get('doctor_id', type=int)
    today = date.today()
    
    query = ProcedureRecord.query.filter(
        ProcedureRecord.status == 'realizado',
        ProcedureRecord.follow_up_due_at.isnot(None),
        ProcedureRecord.follow_up_status.in_(['pending', 'contacted'])
    )
    
    if doctor_id:
        query = query.filter_by(doctor_id=doctor_id)
    elif current_user.is_doctor():
        query = query.filter_by(doctor_id=current_user.id)
    
    records = query.order_by(ProcedureRecord.follow_up_due_at.asc()).limit(100).all()
    
    result = []
    for r in records:
        days_until = (r.follow_up_due_at - today).days if r.follow_up_due_at else 0
        status_label = 'Vencido' if days_until < 0 else ('Próximo' if days_until <= 30 else 'Futuro')
        
        result.append({
            'id': r.id,
            'patient_id': r.patient_id,
            'patient_name': r.patient.name,
            'patient_phone': r.patient.phone,
            'procedure_name': r.procedure_name,
            'performed_date': r.performed_date.isoformat() if r.performed_date else None,
            'follow_up_due_at': r.follow_up_due_at.isoformat() if r.follow_up_due_at else None,
            'follow_up_status': r.follow_up_status,
            'days_until': days_until,
            'urgency': status_label
        })
    
    return jsonify(result)

@crm_bp.route('/api/crm/planned')
@login_required
def get_planned_procedures():
    doctor_id = request.args.get('doctor_id', type=int)
    
    query = ProcedureRecord.query.filter_by(status='planejado')
    
    if doctor_id:
        query = query.filter_by(doctor_id=doctor_id)
    elif current_user.is_doctor():
        query = query.filter_by(doctor_id=current_user.id)
    
    records = query.order_by(ProcedureRecord.created_at.desc()).limit(100).all()
    
    result = []
    for r in records:
        result.append({
            'id': r.id,
            'patient_id': r.patient_id,
            'patient_name': r.patient.name,
            'patient_phone': r.patient.phone,
            'procedure_name': r.procedure_name,
            'planned_date': r.planned_date.isoformat() if r.planned_date else None,
            'notes': r.notes,
            'created_at': r.created_at.isoformat() if r.created_at else None
        })
    
    return jsonify(result)

@crm_bp.route('/api/crm/records', methods=['POST'])
@login_required
def create_procedure_record():
    data = request.get_json()
    
    procedure_name = data.get('procedure_name')
    patient_id = data.get('patient_id')
    status = data.get('status', 'planejado')
    performed_date_str = data.get('performed_date')
    planned_date_str = data.get('planned_date')
    notes = data.get('notes', '')
    
    performed_date = None
    planned_date = None
    follow_up_due_at = None
    
    if performed_date_str:
        performed_date = datetime.strptime(performed_date_str, '%Y-%m-%d').date()
        months = get_follow_up_months(procedure_name)
        follow_up_due_at = performed_date + relativedelta(months=months)
    
    if planned_date_str:
        planned_date = datetime.strptime(planned_date_str, '%Y-%m-%d').date()
    
    record = ProcedureRecord(
        patient_id=patient_id,
        doctor_id=current_user.id,
        procedure_name=procedure_name,
        status=status,
        performed_date=performed_date,
        planned_date=planned_date,
        follow_up_due_at=follow_up_due_at,
        notes=notes
    )
    
    db.session.add(record)
    db.session.commit()
    
    return jsonify({'success': True, 'id': record.id})

@crm_bp.route('/api/crm/records/<int:record_id>', methods=['PATCH'])
@login_required
def update_procedure_record(record_id):
    record = ProcedureRecord.query.get_or_404(record_id)
    data = request.get_json()
    
    if 'status' in data:
        record.status = data['status']
        if data['status'] == 'realizado' and not record.performed_date:
            record.performed_date = date.today()
            months = get_follow_up_months(record.procedure_name)
            record.follow_up_due_at = record.performed_date + relativedelta(months=months)
    
    if 'follow_up_status' in data:
        record.follow_up_status = data['follow_up_status']
    
    if 'notes' in data:
        record.notes = data['notes']
    
    db.session.commit()
    
    return jsonify({'success': True})

@crm_bp.route('/api/crm/stats')
@login_required
def get_crm_stats():
    doctor_id = request.args.get('doctor_id', type=int)
    today = date.today()
    
    base_query = ProcedureRecord.query
    if doctor_id:
        base_query = base_query.filter_by(doctor_id=doctor_id)
    elif current_user.is_doctor():
        base_query = base_query.filter_by(doctor_id=current_user.id)
    
    performed_count = base_query.filter_by(status='realizado').count()
    planned_count = base_query.filter_by(status='planejado').count()
    
    overdue_count = base_query.filter(
        ProcedureRecord.status == 'realizado',
        ProcedureRecord.follow_up_due_at < today,
        ProcedureRecord.follow_up_status.in_(['pending', 'contacted'])
    ).count()
    
    due_soon_count = base_query.filter(
        ProcedureRecord.status == 'realizado',
        ProcedureRecord.follow_up_due_at >= today,
        ProcedureRecord.follow_up_due_at <= today + timedelta(days=30),
        ProcedureRecord.follow_up_status.in_(['pending', 'contacted'])
    ).count()
    
    return jsonify({
        'performed': performed_count,
        'planned': planned_count,
        'overdue': overdue_count,
        'due_soon': due_soon_count
    })
