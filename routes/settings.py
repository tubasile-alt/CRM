"""
Rotas de Configurações do Sistema
"""
from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from models import db, OperatingRoom, DoctorPreference, User
from utils.backup import BackupManager

settings_bp = Blueprint('settings', __name__, url_prefix='/configuracoes')
backup_manager = BackupManager()

@settings_bp.route('/')
@login_required
def index():
    """Página de configurações"""
    if not current_user.is_doctor():
        return jsonify({'error': 'Apenas médicos podem acessar configurações'}), 403
    
    rooms = OperatingRoom.query.all()
    doctors = User.query.filter_by(role='medico').all()
    
    return render_template('settings.html', rooms=rooms, doctors=doctors)

@settings_bp.route('/api/rooms', methods=['GET'])
@login_required
def get_rooms():
    """Lista todas as salas"""
    rooms = OperatingRoom.query.all()
    return jsonify([{
        'id': r.id,
        'name': r.name,
        'capacity': r.capacity,
        'is_active': r.is_active
    } for r in rooms])

@settings_bp.route('/api/rooms', methods=['POST'])
@login_required
def create_room():
    """Cria nova sala"""
    if not current_user.is_doctor():
        return jsonify({'error': 'Sem permissão'}), 403
    
    data = request.json
    room = OperatingRoom(
        name=data['name'],
        capacity=data.get('capacity', 1),
        is_active=data.get('is_active', True)
    )
    
    db.session.add(room)
    db.session.commit()
    
    return jsonify({'success': True, 'room': {
        'id': room.id,
        'name': room.name,
        'capacity': room.capacity,
        'is_active': room.is_active
    }})

@settings_bp.route('/api/rooms/<int:room_id>', methods=['PUT'])
@login_required
def update_room(room_id):
    """Atualiza sala"""
    if not current_user.is_doctor():
        return jsonify({'error': 'Sem permissão'}), 403
    
    room = OperatingRoom.query.get(room_id)
    if not room:
        return jsonify({'error': 'Sala não encontrada'}), 404
    
    data = request.json
    if 'name' in data:
        room.name = data['name']
    if 'capacity' in data:
        room.capacity = data['capacity']
    if 'is_active' in data:
        room.is_active = data['is_active']
    
    db.session.commit()
    return jsonify({'success': True})

@settings_bp.route('/api/rooms/<int:room_id>', methods=['DELETE'])
@login_required
def delete_room(room_id):
    """Deleta sala"""
    if not current_user.is_doctor():
        return jsonify({'error': 'Sem permissão'}), 403
    
    room = OperatingRoom.query.get(room_id)
    if not room:
        return jsonify({'error': 'Sala não encontrada'}), 404
    
    db.session.delete(room)
    db.session.commit()
    return jsonify({'success': True})

@settings_bp.route('/api/doctor-preferences', methods=['GET'])
@login_required
def get_doctor_preferences():
    """Lista preferências dos médicos"""
    doctors = User.query.filter_by(role='medico').all()
    result = []
    
    for doctor in doctors:
        pref = DoctorPreference.query.filter_by(user_id=doctor.id).first()
        result.append({
            'doctor_id': doctor.id,
            'doctor_name': doctor.name,
            'color': pref.color if pref else '#0d6efd',
            'layer_enabled': pref.layer_enabled if pref else True
        })
    
    return jsonify(result)

@settings_bp.route('/api/doctor-preferences', methods=['POST'])
@login_required
def update_doctor_preferences():
    """Atualiza preferências de médico"""
    if not current_user.is_doctor():
        return jsonify({'error': 'Sem permissão'}), 403
    
    data = request.json
    doctor_id = data.get('doctor_id')
    
    # Apenas o próprio médico pode alterar suas preferências
    if doctor_id != current_user.id:
        return jsonify({'error': 'Sem permissão'}), 403
    
    pref = DoctorPreference.query.filter_by(user_id=doctor_id).first()
    
    if not pref:
        pref = DoctorPreference(user_id=doctor_id)
        db.session.add(pref)
    
    if 'color' in data:
        pref.color = data['color']
    if 'layer_enabled' in data:
        pref.layer_enabled = data['layer_enabled']
    
    db.session.commit()
    return jsonify({'success': True})

@settings_bp.route('/api/backup/create', methods=['POST'])
@login_required
def create_backup():
    """Cria backup do banco de dados"""
    if not current_user.is_doctor():
        return jsonify({'error': 'Sem permissão'}), 403
    
    try:
        backup_path = backup_manager.create_backup(compress=True)
        return jsonify({
            'success': True,
            'message': 'Backup criado com sucesso',
            'backup_path': backup_path
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@settings_bp.route('/api/backup/list', methods=['GET'])
@login_required
def list_backups():
    """Lista backups disponíveis"""
    if not current_user.is_doctor():
        return jsonify({'error': 'Sem permissão'}), 403
    
    backups = backup_manager.list_backups()
    stats = backup_manager.get_backup_stats()
    
    return jsonify({
        'backups': [{
            'filename': b['filename'],
            'size': b['size'],
            'modified': b['modified'].isoformat(),
            'compressed': b['compressed']
        } for b in backups],
        'stats': stats
    })
