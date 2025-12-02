from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from models import db, TransplantSurgeryRecord, SurgeryEvolution
from datetime import datetime

patient_bp = Blueprint('patient', __name__, url_prefix='/api/patient')

@patient_bp.route('/<int:patient_id>/surgeries', methods=['GET'])
@login_required
def get_patient_surgeries(patient_id):
    """Listar todas as cirurgias de um paciente com suas evoluções"""
    try:
        surgeries = TransplantSurgeryRecord.query.filter_by(patient_id=patient_id).order_by(TransplantSurgeryRecord.surgery_date.desc()).all()
        result = []
        for s in surgeries:
            try:
                evolutions = SurgeryEvolution.query.filter_by(surgery_id=s.id).order_by(SurgeryEvolution.evolution_date.desc()).all()
            except:
                evolutions = []
            result.append({
                'id': s.id,
                'surgery_date': s.surgery_date.strftime('%d/%m/%Y'),
                'surgery_date_iso': s.surgery_date.isoformat(),
                'surgical_data': s.surgical_data,
                'observations': s.observations,
                'doctor_name': s.doctor.name,
                'evolutions': [{
                    'id': e.id,
                    'date': e.evolution_date.strftime('%d/%m/%Y %H:%M'),
                    'content': e.content,
                    'doctor': e.doctor.name
                } for e in evolutions]
            })
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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

@patient_bp.route('/delete/<int:surgery_id>', methods=['DELETE'])
@login_required
def delete_patient_surgery(surgery_id):
    """Deletar uma cirurgia"""
    if not current_user.is_doctor():
        return jsonify({'success': False, 'error': 'Apenas médicos'}), 403
    
    surgery = TransplantSurgeryRecord.query.get_or_404(surgery_id)
    if surgery.doctor_id != current_user.id and not current_user.is_admin():
        return jsonify({'success': False, 'error': 'Não autorizado'}), 403
    
    db.session.delete(surgery)
    db.session.commit()
    
    return jsonify({'success': True})

@patient_bp.route('/<int:patient_id>/surgery/<int:surgery_id>/evolution', methods=['POST'])
@login_required
def create_surgery_evolution(patient_id, surgery_id):
    """Criar uma evolução para uma cirurgia"""
    if not current_user.is_doctor():
        return jsonify({'success': False, 'error': 'Apenas médicos'}), 403
    
    surgery = TransplantSurgeryRecord.query.get_or_404(surgery_id)
    if surgery.patient_id != patient_id:
        return jsonify({'success': False, 'error': 'Cirurgia não pertence ao paciente'}), 400
    
    data = request.get_json()
    content = data.get('content', '').strip()
    
    if not content:
        return jsonify({'success': False, 'error': 'Conteúdo da evolução não pode estar vazio'}), 400
    
    evolution = SurgeryEvolution(
        surgery_id=surgery_id,
        doctor_id=current_user.id,
        content=content
    )
    db.session.add(evolution)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'id': evolution.id,
        'date': evolution.evolution_date.strftime('%d/%m/%Y %H:%M'),
        'content': evolution.content,
        'doctor': evolution.doctor.name
    })

@patient_bp.route('/surgery-evolution/<int:evolution_id>', methods=['DELETE'])
@login_required
def delete_surgery_evolution(evolution_id):
    """Deletar uma evolução de cirurgia"""
    if not current_user.is_doctor():
        return jsonify({'success': False, 'error': 'Apenas médicos'}), 403
    
    evolution = SurgeryEvolution.query.get_or_404(evolution_id)
    if evolution.doctor_id != current_user.id and not current_user.is_admin():
        return jsonify({'success': False, 'error': 'Não autorizado'}), 403
    
    db.session.delete(evolution)
    db.session.commit()
    
    return jsonify({'success': True})

