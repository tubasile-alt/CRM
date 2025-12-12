"""
Rotas de gerenciamento de espera (Check-in/Check-out)
"""
from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from services.waiting_service import WaitingService
import pytz

waiting_room_bp = Blueprint('waiting_room', __name__, url_prefix='/espera')
waiting_service = WaitingService()

@waiting_room_bp.route('/api/checkin/<int:appointment_id>', methods=['POST'])
@login_required
def check_in(appointment_id):
    """Realiza check-in de um paciente"""
    try:
        result = waiting_service.check_in(appointment_id)
        return jsonify({'success': True, 'data': result})
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Erro ao realizar check-in'}), 500

@waiting_room_bp.route('/api/checkout/<int:appointment_id>', methods=['POST'])
@login_required
def check_out(appointment_id):
    """Realiza check-out de um paciente"""
    try:
        result = waiting_service.check_out(appointment_id)
        return jsonify({'success': True, 'data': result})
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Erro ao realizar check-out'}), 500

@waiting_room_bp.route('/api/list', methods=['GET'])
@login_required
def get_waiting_list():
    """Retorna lista de pacientes em espera"""
    doctor_id = request.args.get('doctor_id', type=int)
    date_str = request.args.get('date')
    
    date = None
    if date_str:
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
    
    # Se não for médico e não especificou doctor_id, pega todos
    if not doctor_id and current_user.is_doctor():
        doctor_id = current_user.id
    
    waiting_list = waiting_service.get_waiting_list(doctor_id, date)
    stats = waiting_service.get_wait_stats(doctor_id, date)
    
    return jsonify({
        'waiting_list': waiting_list,
        'stats': stats
    })

@waiting_room_bp.route('/api/assign-room/<int:appointment_id>', methods=['POST'])
@login_required
def assign_room(appointment_id):
    """Atribui sala a um paciente"""
    data = request.json or {}
    room_name = data.get('room')
    
    if not room_name:
        return jsonify({'error': 'Sala não informada'}), 400
    
    try:
        result = waiting_service.assign_room(appointment_id, room_name)
        return jsonify({'success': True, 'data': result})
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Erro ao atribuir sala'}), 500

@waiting_room_bp.route('/api/remove/<int:appointment_id>', methods=['POST'])
@login_required
def remove_from_waiting(appointment_id):
    """Remove paciente da lista de espera (desfazer check-in)"""
    try:
        result = waiting_service.check_out(appointment_id)
        return jsonify({'success': True, 'data': result})
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Erro ao remover da lista'}), 500

@waiting_room_bp.route('/api/stats', methods=['GET'])
@login_required
def get_stats():
    """Retorna estatísticas de espera"""
    doctor_id = request.args.get('doctor_id', type=int)
    date_str = request.args.get('date')
    
    date = None
    if date_str:
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
    
    if not doctor_id and current_user.is_doctor():
        doctor_id = current_user.id
    
    stats = waiting_service.get_wait_stats(doctor_id, date)
    
    return jsonify(stats)

@waiting_room_bp.route('/api/average-wait', methods=['GET'])
@login_required
def get_average_wait():
    """Retorna tempo médio de espera"""
    doctor_id = request.args.get('doctor_id', type=int)
    days = request.args.get('days', default=30, type=int)
    
    if not doctor_id and current_user.is_doctor():
        doctor_id = current_user.id
    
    stats = waiting_service.get_average_wait_time(doctor_id, days)
    
    return jsonify(stats)
