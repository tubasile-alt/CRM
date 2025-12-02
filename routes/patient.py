from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from models import db, TransplantSurgeryRecord
from datetime import datetime

patient_bp = Blueprint('patient', __name__, url_prefix='/api/patient')

@patient_bp.route('/<int:patient_id>/surgeries', methods=['GET'])
@login_required
def get_patient_surgeries(patient_id):
    """Listar todas as cirurgias de um paciente"""
    surgeries = TransplantSurgeryRecord.query.filter_by(patient_id=patient_id).order_by(TransplantSurgeryRecord.surgery_date.desc()).all()
    return jsonify([{
        'id': s.id,
        'surgery_date': s.surgery_date.strftime('%d/%m/%Y'),
        'surgery_date_iso': s.surgery_date.isoformat(),
        'surgical_data': s.surgical_data,
        'observations': s.observations,
        'doctor_name': s.doctor.name
    } for s in surgeries])

@patient_bp.route('/<int:patient_id>/surgery', methods=['POST'])
@login_required
def create_patient_surgery(patient_id):
    """Criar nova cirurgia para um paciente"""
    if not current_user.is_doctor():
        return jsonify({'success': False, 'error': 'Apenas médicos'}), 403
    
    data = request.get_json()
    
    try:
        surgery_date = datetime.strptime(data.get('surgery_date'), '%Y-%m-%d').date()
    except:
        return jsonify({'success': False, 'error': 'Data inválida'}), 400
    
    surgery = TransplantSurgeryRecord(
        patient_id=patient_id,
        doctor_id=current_user.id,
        surgery_date=surgery_date,
        surgical_data=data.get('surgical_data', ''),
        observations=data.get('observations', '')
    )
    db.session.add(surgery)
    db.session.commit()
    
    return jsonify({'success': True, 'id': surgery.id})

