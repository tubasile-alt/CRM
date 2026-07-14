from datetime import datetime

from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required

from models import Appointment, Evolution, db
from services.access_control import can_manage_owned_record
from services.clinic_time import get_brazil_time


evolutions_api_bp = Blueprint('evolutions_api', __name__)


@evolutions_api_bp.route('/api/patient/<int:patient_id>/evolutions', methods=['GET'])
@login_required
def get_evolutions(patient_id):
    """Listar todas as evoluções agrupadas por consulta"""
    from models import Appointment
    
    # Buscar todas as consultas do paciente
    consultations = Appointment.query.filter_by(patient_id=patient_id).order_by(Appointment.start_time.asc()).all()
    
    # Rastrear consultation_ids com evoluções
    consultation_ids_with_evolutions = set()
    
    result = []
    
    for consultation in consultations:
        # Buscar evoluções desta consulta
        evolutions = Evolution.query.filter_by(consultation_id=consultation.id).order_by(Evolution.evolution_date.asc()).all()
        
        effective_date = consultation.consultation_date or consultation.start_time
        consultation_data = {
            'id': consultation.id,
            'date': effective_date.strftime('%d/%m/%Y %H:%M'),
            'category': consultation.appointment_type or 'Consulta',
            'doctor_name': consultation.doctor.name if consultation.doctor else 'N/A',
            'status': consultation.status,
            'evolutions': []
        }
        
        for evo in evolutions:
            consultation_ids_with_evolutions.add(consultation.id)
            consultation_data['evolutions'].append({
                'id': evo.id,
                'date': evo.evolution_date.strftime('%d/%m/%Y %H:%M'),
                'content': evo.content,
                'doctor': evo.doctor.name,
                'evolution_date': evo.evolution_date.isoformat()
            })
        
        result.append(consultation_data)
    
    # Inverter para mostrar mais recente primeiro
    result.reverse()
    
    # Buscar evoluções sem consultation_id (orphaned)
    orphaned_evolutions = Evolution.query.filter_by(patient_id=patient_id, consultation_id=None).order_by(Evolution.evolution_date.desc()).all()
    
    if orphaned_evolutions and result:
        # IMPORTANTE: Anexar evoluções órfãs à consulta mais RECENTE (result[0])
        # Mesmo que ela não esteja com status 'atendido' ainda
        target_entry = result[0]
            
        for evo in orphaned_evolutions:
            # Evitar duplicatas se já foi adicionada por algum motivo
            if not any(e['id'] == evo.id for e in target_entry['evolutions']):
                target_entry['evolutions'].append({
                    'id': evo.id,
                    'date': evo.evolution_date.strftime('%d/%m/%Y %H:%M'),
                    'content': evo.content,
                    'doctor': evo.doctor.name,
                    'evolution_date': evo.evolution_date.isoformat()
                })
        target_entry['evolutions'].sort(key=lambda x: x['evolution_date'])
    
    return jsonify(result)


@evolutions_api_bp.route('/api/patient/<int:patient_id>/evolution', methods=['POST'])
@login_required
def create_evolution(patient_id):
    """Criar nova evolução"""
    if not current_user.is_doctor():
        return jsonify({'success': False, 'error': 'Apenas médicos'}), 403
    
    data = request.get_json()
    if not data or 'content' not in data:
        return jsonify({'success': False, 'error': 'Conteúdo vazio'}), 400
    
    evolution_date = data.get('evolution_date')
    if evolution_date:
        try:
            evolution_date = datetime.fromisoformat(evolution_date)
        except:
            evolution_date = get_brazil_time()
    else:
        evolution_date = get_brazil_time()
    
    # Validar consultation_id se fornecido
    consultation_id = data.get('consultation_id')
    if consultation_id:
        try:
            consultation_id = int(consultation_id)
            # Verificar se o appointment existe e pertence ao paciente
            appointment = Appointment.query.filter_by(id=consultation_id, patient_id=patient_id).first()
            if not appointment:
                consultation_id = None  # Se não existe, deixar como NULL
        except (ValueError, TypeError):
            consultation_id = None
    
    evo = Evolution(
        patient_id=patient_id,
        doctor_id=current_user.id,
        evolution_date=evolution_date,
        consultation_id=consultation_id,
        content=data['content']
    )
    db.session.add(evo)
    db.session.commit()
    
    return jsonify({'success': True, 'id': evo.id})


@evolutions_api_bp.route('/api/evolution/<int:evo_id>', methods=['PUT'])
@login_required
def update_evolution(evo_id):
    """Editar evolução"""
    evo = Evolution.query.get_or_404(evo_id)
    if not can_manage_owned_record(current_user, evo.doctor_id):
        return jsonify({'success': False, 'error': 'Não autorizado'}), 403
    
    data = request.get_json()
    if 'content' in data:
        evo.content = data['content']
    if 'evolution_date' in data:
        try:
            evo.evolution_date = datetime.fromisoformat(data['evolution_date'])
        except:
            pass
    
    db.session.commit()
    return jsonify({'success': True})


@evolutions_api_bp.route('/api/evolution/<int:evo_id>', methods=['DELETE'])
@login_required
def delete_evolution(evo_id):
    """Deletar evolução"""
    evo = Evolution.query.get_or_404(evo_id)
    if not can_manage_owned_record(current_user, evo.doctor_id):
        return jsonify({'success': False, 'error': 'Não autorizado'}), 403
    
    db.session.delete(evo)
    db.session.commit()
    return jsonify({'success': True})
