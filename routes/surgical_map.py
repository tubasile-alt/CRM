"""
Rotas do Mapa Cirúrgico
"""
from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from models import db, Surgery, OperatingRoom, User
from services.surgery_service import SurgeryService
from services.email_service import EmailService
from utils.exports.pdf_export import PDFExporter
from utils.exports.excel_export import ExcelExporter
import pytz

surgical_map_bp = Blueprint('surgical_map', __name__, url_prefix='/mapa-cirurgico')
surgery_service = SurgeryService()

@surgical_map_bp.route('/')
@login_required
def index():
    """Página principal do mapa cirúrgico"""
    # Pegar a segunda-feira da semana atual
    today = datetime.now(pytz.timezone('America/Sao_Paulo')).date()
    week_start = today - timedelta(days=today.weekday())
    
    return render_template('surgical_map.html', week_start=week_start)

@surgical_map_bp.route('/api/weekly', methods=['GET'])
@login_required
def get_weekly_map():
    """Retorna mapa cirúrgico semanal"""
    week_start_str = request.args.get('week_start')
    
    if week_start_str:
        week_start = datetime.strptime(week_start_str, '%Y-%m-%d').date()
    else:
        today = datetime.now(pytz.timezone('America/Sao_Paulo')).date()
        week_start = today - timedelta(days=today.weekday())
    
    map_data = surgery_service.get_weekly_map(week_start)
    
    # Serializar para JSON
    result = {
        'week_start': week_start.isoformat(),
        'week_end': map_data['week_end'].isoformat(),
        'rooms': []
    }
    
    for room_id, data in map_data['rooms'].items():
        room_data = {
            'id': data['room'].id,
            'name': data['room'].name,
            'capacity': data['room'].capacity,
            'surgeries': []
        }
        
        for surgery in data['surgeries']:
            # Calcular duração em minutos
            start_dt = datetime.combine(datetime.today(), surgery.start_time)
            end_dt = datetime.combine(datetime.today(), surgery.end_time)
            duration_minutes = int((end_dt - start_dt).total_seconds() / 60)
            
            room_data['surgeries'].append({
                'id': surgery.id,
                'doctor_id': surgery.doctor_id,
                'doctor_name': surgery.doctor.name,
                'patient_name': surgery.patient_name,
                'procedure_name': surgery.procedure_name,
                'date': surgery.date.isoformat(),
                'start_time': surgery.start_time.strftime('%H:%M'),
                'end_time': surgery.end_time.strftime('%H:%M'),
                'duration_minutes': duration_minutes,
                'status': surgery.status,
                'notes': surgery.notes
            })
        
        result['rooms'].append(room_data)
    
    return jsonify(result)

@surgical_map_bp.route('/api/surgery', methods=['POST'])
@login_required
def create_surgery():
    """Cria nova cirurgia"""
    if not current_user.is_doctor():
        return jsonify({'error': 'Apenas médicos podem criar cirurgias'}), 403
    
    data = request.json
    
    try:
        date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        start_time = datetime.strptime(data['start_time'], '%H:%M').time()
        
        surgery = surgery_service.create_surgery(
            doctor_id=current_user.id,
            patient_name=data['patient_name'],
            procedure_name=data['procedure_name'],
            operating_room_id=data['operating_room_id'],
            date=date,
            start_time=start_time,
            duration_minutes=data['duration_minutes'],
            notes=data.get('notes'),
            created_by=current_user.id
        )
        
        # Calcular duração
        start_dt = datetime.combine(datetime.today(), surgery.start_time)
        end_dt = datetime.combine(datetime.today(), surgery.end_time)
        duration_minutes = int((end_dt - start_dt).total_seconds() / 60)
        
        return jsonify({
            'success': True,
            'surgery': {
                'id': surgery.id,
                'doctor_name': surgery.doctor.name,
                'patient_name': surgery.patient_name,
                'procedure_name': surgery.procedure_name,
                'date': surgery.date.isoformat(),
                'start_time': surgery.start_time.strftime('%H:%M'),
                'end_time': surgery.end_time.strftime('%H:%M'),
                'duration_minutes': duration_minutes,
                'status': surgery.status
            }
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Erro ao criar cirurgia'}), 500

@surgical_map_bp.route('/api/surgery/<int:surgery_id>', methods=['PUT'])
@login_required
def update_surgery(surgery_id):
    """Atualiza cirurgia"""
    surgery = Surgery.query.get(surgery_id)
    if not surgery:
        return jsonify({'error': 'Cirurgia não encontrada'}), 404
    
    if not current_user.is_doctor() or surgery.doctor_id != current_user.id:
        return jsonify({'error': 'Sem permissão'}), 403
    
    data = request.json
    updates = {}
    
    if 'patient_name' in data:
        updates['patient_name'] = data['patient_name']
    if 'procedure_name' in data:
        updates['procedure_name'] = data['procedure_name']
    if 'operating_room_id' in data:
        updates['operating_room_id'] = data['operating_room_id']
    if 'date' in data:
        updates['date'] = datetime.strptime(data['date'], '%Y-%m-%d').date()
    if 'start_time' in data:
        updates['start_time'] = datetime.strptime(data['start_time'], '%H:%M').time()
    if 'duration_minutes' in data:
        updates['duration_minutes'] = data['duration_minutes']
    if 'status' in data:
        updates['status'] = data['status']
    if 'notes' in data:
        updates['notes'] = data['notes']
    if 'updated_by' not in updates:
        updates['updated_by'] = current_user.id
    
    try:
        surgery = surgery_service.update_surgery(surgery_id, **updates)
        return jsonify({'success': True})
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

@surgical_map_bp.route('/api/surgery/<int:surgery_id>', methods=['DELETE'])
@login_required
def delete_surgery(surgery_id):
    """Deleta cirurgia"""
    surgery = Surgery.query.get(surgery_id)
    if not surgery:
        return jsonify({'error': 'Cirurgia não encontrada'}), 404
    
    if not current_user.is_doctor() or surgery.doctor_id != current_user.id:
        return jsonify({'error': 'Sem permissão'}), 403
    
    try:
        surgery_service.delete_surgery(surgery_id)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@surgical_map_bp.route('/export/pdf', methods=['GET'])
@login_required
def export_pdf():
    """Exporta mapa cirúrgico em PDF"""
    week_start_str = request.args.get('week_start')
    week_start = datetime.strptime(week_start_str, '%Y-%m-%d').date() if week_start_str else datetime.now().date()
    
    map_data = surgery_service.get_weekly_map(week_start)
    rooms = OperatingRoom.query.all()
    
    exporter = PDFExporter()
    pdf_buffer = exporter.export_surgical_map(map_data['all_surgeries'], week_start, rooms)
    
    return pdf_buffer.getvalue(), 200, {
        'Content-Type': 'application/pdf',
        'Content-Disposition': f'attachment; filename=mapa_cirurgico_{week_start.strftime("%Y%m%d")}.pdf'
    }

@surgical_map_bp.route('/export/excel', methods=['GET'])
@login_required
def export_excel():
    """Exporta mapa cirúrgico em Excel"""
    week_start_str = request.args.get('week_start')
    week_start = datetime.strptime(week_start_str, '%Y-%m-%d').date() if week_start_str else datetime.now().date()
    
    map_data = surgery_service.get_weekly_map(week_start)
    rooms = OperatingRoom.query.all()
    
    exporter = ExcelExporter()
    excel_buffer = exporter.export_surgical_map(map_data['all_surgeries'], week_start, rooms)
    
    return excel_buffer.getvalue(), 200, {
        'Content-Type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'Content-Disposition': f'attachment; filename=mapa_cirurgico_{week_start.strftime("%Y%m%d")}.xlsx'
    }
