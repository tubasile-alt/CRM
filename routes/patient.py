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
                'surgery_type': s.surgery_type or '',
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
        surgery_type=data.get('surgery_type', ''),
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

@patient_bp.route('/<int:patient_id>/surgery/<int:surgery_id>/evolutions', methods=['GET'])
@login_required
def get_surgery_evolutions(patient_id, surgery_id):
    """Listar evoluções de uma cirurgia específica"""
    surgery = TransplantSurgeryRecord.query.get_or_404(surgery_id)
    if surgery.patient_id != patient_id:
        return jsonify({'error': 'Cirurgia não pertence ao paciente'}), 400
    
    evolutions = SurgeryEvolution.query.filter_by(surgery_id=surgery_id).order_by(SurgeryEvolution.evolution_date.desc()).all()
    return jsonify({
        'evolutions': [{
            'id': e.id,
            'evolution_date': e.evolution_date.isoformat(),
            'content': e.content,
            'evolution_type': e.evolution_type if hasattr(e, 'evolution_type') else 'general',
            'has_necrosis': e.has_necrosis if hasattr(e, 'has_necrosis') else False,
            'has_scabs': e.has_scabs if hasattr(e, 'has_scabs') else False,
            'has_infection': e.has_infection if hasattr(e, 'has_infection') else False,
            'has_follicle_loss': e.has_follicle_loss if hasattr(e, 'has_follicle_loss') else False,
            'result_rating': e.result_rating if hasattr(e, 'result_rating') else None,
            'needs_another_surgery': e.needs_another_surgery if hasattr(e, 'needs_another_surgery') else False,
            'doctor_name': e.doctor.name
        } for e in evolutions]
    })

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

# --- Transplante capilar: resumo do planejamento (para visualização rápida em Evolução / secretária) ---
@patient_bp.route('/<int:patient_id>/transplant/schedule-surgery', methods=['POST'])
@login_required
def schedule_transplant_surgery(patient_id):
    """Agenda uma cirurgia baseada no último planejamento"""
    from models import Patient, HairTransplant, TransplantSurgeryRecord, Note
    from services.calendar_service import create_transplant_surgery_event
    
    data = request.get_json()
    surgery_date_str = data.get('surgery_date')
    right_card_snapshot = (data.get('right_card_snapshot') or '').strip()
    
    if not surgery_date_str:
        return jsonify({'success': False, 'error': 'Data da cirurgia é obrigatória'}), 400
        
    try:
        surgery_date = datetime.strptime(surgery_date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'success': False, 'error': 'Formato de data inválido (YYYY-MM-DD)'}), 400
    
    patient = Patient.query.get_or_404(patient_id)
    
    # Buscar último planejamento
    planning = (HairTransplant.query
               .join(Note, HairTransplant.note_id == Note.id)
               .filter(Note.patient_id == patient_id)
               .order_by(HairTransplant.id.desc())
               .first())
               
    planning_text = planning.surgical_planning if planning else "Nenhum planejamento encontrado."
    
    # Criar ou atualizar registro de cirurgia
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Scheduling surgery for patient {patient_id} on {surgery_date}")
    
    surgery = TransplantSurgeryRecord.query.filter_by(
        patient_id=patient_id, 
        surgery_date=surgery_date
    ).first()
    
    if not surgery:
        logger.info("Creating new surgery record")
        surgery = TransplantSurgeryRecord(
            patient_id=patient_id,
            doctor_id=current_user.id,
            surgery_date=surgery_date,
            status="scheduled",
            planning_snapshot=planning_text
        )
        db.session.add(surgery)
    else:
        logger.info("Updating existing surgery record")
        surgery.status = "scheduled"
        surgery.planning_snapshot = planning_text
    
    db.session.commit()
    
    # Criar evento no Google Calendar
    logger.info("Creating Google Calendar event")
    cal_ok, cal_result = create_transplant_surgery_event(
        patient_name=patient.name,
        surgery_date=surgery_date,
        planning_snapshot=planning_text,
        phone=patient.phone,
        cpf=patient.cpf,
        right_card_snapshot=right_card_snapshot
    )
    
    if cal_ok:
        logger.info(f"Calendar event created: {cal_result}")
        surgery.calendar_event_id = cal_result
        db.session.commit()
    else:
        logger.error(f"Failed to create calendar event: {cal_result}")
    
    return jsonify({
        'success': True, 
        'id': surgery.id,
        'calendar_event_created': cal_ok,
        'calendar_event_id': cal_result if cal_ok else None,
        'calendar_error': cal_result if not cal_ok else None
    })

@patient_bp.route('/<int:patient_id>/transplant/planning-summary', methods=['GET'])
@login_required
def get_transplant_planning_summary(patient_id):
    """
    Retorna:
      - último planejamento cirúrgico preenchido (HairTransplant.surgical_planning)
      - última data de cirurgia registrada (TransplantSurgeryRecord.surgery_date)
    O front decide exibir/ocultar o card.
    """
    try:
        from flask import jsonify
        from models import HairTransplant, Note, TransplantSurgeryRecord

        # 1) Último planejamento preenchido
        planning_text = ""
        planning_note_id = None

        items = (HairTransplant.query
                 .join(Note, HairTransplant.note_id == Note.id)
                 .filter(Note.patient_id == patient_id)
                 .order_by(HairTransplant.id.desc())
                 .all())

        for item in items:
            txt = (getattr(item, "surgical_planning", "") or "").strip()
            if txt:
                planning_text = txt
                planning_note_id = getattr(item, "note_id", None)
                break

        # 2) Última cirurgia (se existir)
        last_surgery = (TransplantSurgeryRecord.query
                        .filter_by(patient_id=patient_id)
                        .order_by(TransplantSurgeryRecord.surgery_date.desc())
                        .first())

        last_surgery_str = last_surgery.surgery_date.strftime('%d/%m/%Y') if last_surgery and last_surgery.surgery_date else None
        last_surgery_iso = last_surgery.surgery_date.isoformat() if last_surgery and last_surgery.surgery_date else None

        return jsonify({
            "success": True,
            "has_planning": bool(planning_text),
            "planning": planning_text,
            "planning_note_id": planning_note_id,
            "last_surgery_date": last_surgery_str,
            "last_surgery_date_iso": last_surgery_iso
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
