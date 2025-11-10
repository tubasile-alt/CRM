from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta, date
import pytz
import click

from config import Config
from models import db, User, Patient, Appointment, Note, Procedure, Indication, Tag, PatientTag, ChatMessage

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
csrf = CSRFProtect(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Por favor, faça login para acessar esta página.'

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

def get_brazil_time():
    tz = pytz.timezone('America/Sao_Paulo')
    return datetime.now(tz)

@app.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.is_doctor():
            return redirect(url_for('dashboard'))
        else:
            return redirect(url_for('agenda'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            login_user(user, remember=True)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        else:
            flash('Email ou senha incorretos.', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

def get_doctor_id():
    """Retorna o ID do médico - se o usuário atual é médico, retorna seu ID,
    se é secretária, retorna o ID do primeiro médico (assumindo clínica com um médico)"""
    if current_user.is_doctor():
        return current_user.id
    else:
        doctor = User.query.filter_by(role='medico').first()
        return doctor.id if doctor else None

@app.route('/dashboard')
@login_required
def dashboard():
    if not current_user.is_doctor():
        return redirect(url_for('agenda'))
    
    today = get_brazil_time().date()
    
    appointments = Appointment.query.filter(
        db.func.date(Appointment.start_time) == today,
        Appointment.doctor_id == current_user.id
    ).all()
    
    stats = {
        'agendados': sum(1 for a in appointments if a.status == 'agendado'),
        'confirmados': sum(1 for a in appointments if a.status == 'confirmado'),
        'atendidos': sum(1 for a in appointments if a.status == 'atendido'),
        'faltaram': sum(1 for a in appointments if a.status == 'faltou')
    }
    
    return render_template('dashboard.html', stats=stats)

@app.route('/agenda')
@login_required
def agenda():
    return render_template('agenda.html')

@app.route('/api/appointments')
@login_required
def get_appointments():
    doctor_id = get_doctor_id()
    if not doctor_id:
        return jsonify([])
    
    appointments = Appointment.query.filter_by(doctor_id=doctor_id).all()
    
    events = []
    for apt in appointments:
        color = {
            'agendado': '#6c757d',
            'confirmado': '#0d6efd',
            'atendido': '#198754',
            'faltou': '#dc3545'
        }.get(apt.status, '#6c757d')
        
        events.append({
            'id': apt.id,
            'title': apt.patient.name,
            'start': apt.start_time.isoformat(),
            'end': apt.end_time.isoformat(),
            'backgroundColor': color,
            'borderColor': color,
            'extendedProps': {
                'status': apt.status,
                'patientId': apt.patient_id,
                'phone': apt.patient.phone or '',
                'notes': apt.notes or ''
            }
        })
    
    return jsonify(events)

@app.route('/api/appointments', methods=['POST'])
@login_required
def create_appointment():
    data = request.json
    
    doctor_id = get_doctor_id()
    if not doctor_id:
        return jsonify({'success': False, 'error': 'Médico não encontrado'}), 400
    
    patient = Patient.query.filter_by(name=data['patientName']).first()
    if not patient:
        patient = Patient(
            name=data['patientName'],
            phone=data.get('phone', ''),
            email=data.get('email', '')
        )
        db.session.add(patient)
        db.session.flush()
    
    appointment = Appointment(
        patient_id=patient.id,
        doctor_id=doctor_id,
        start_time=datetime.fromisoformat(data['start']),
        end_time=datetime.fromisoformat(data['end']),
        status=data.get('status', 'agendado'),
        notes=data.get('notes', '')
    )
    
    db.session.add(appointment)
    db.session.commit()
    
    return jsonify({'success': True, 'id': appointment.id})

@app.route('/api/appointments/<int:id>', methods=['PUT'])
@login_required
def update_appointment(id):
    appointment = Appointment.query.get_or_404(id)
    data = request.json
    
    if 'start' in data:
        appointment.start_time = datetime.fromisoformat(data['start'])
    if 'end' in data:
        appointment.end_time = datetime.fromisoformat(data['end'])
    if 'status' in data:
        appointment.status = data['status']
    if 'notes' in data:
        appointment.notes = data['notes']
    
    db.session.commit()
    
    return jsonify({'success': True})

@app.route('/api/appointments/<int:id>', methods=['DELETE'])
@login_required
def delete_appointment(id):
    appointment = Appointment.query.get_or_404(id)
    db.session.delete(appointment)
    db.session.commit()
    
    return jsonify({'success': True})

@app.route('/prontuario/<int:patient_id>')
@login_required
def prontuario(patient_id):
    if not current_user.is_doctor():
        return redirect(url_for('agenda'))
    
    patient = Patient.query.get_or_404(patient_id)
    procedures = Procedure.query.all()
    tags = Tag.query.all()
    patient_tags = [pt.tag_id for pt in patient.tags]
    
    notes = Note.query.filter_by(patient_id=patient_id).order_by(Note.created_at.desc()).all()
    
    return render_template('prontuario.html', 
                         patient=patient, 
                         procedures=procedures,
                         tags=tags,
                         patient_tags=patient_tags,
                         notes=notes)

@app.route('/api/prontuario/<int:patient_id>', methods=['POST'])
@login_required
def save_prontuario(patient_id):
    if not current_user.is_doctor():
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403
    
    data = request.json
    
    note = Note(
        patient_id=patient_id,
        doctor_id=current_user.id,
        note_type=data['type'],
        content=data['content'],
        consultation_duration=data.get('duration')
    )
    
    db.session.add(note)
    db.session.flush()
    
    if 'indicated_procedures' in data:
        for proc_id in data['indicated_procedures']:
            indication = Indication(
                note_id=note.id,
                procedure_id=proc_id,
                indicated=True,
                performed=False
            )
            db.session.add(indication)
    
    if 'performed_procedures' in data:
        for proc_id in data['performed_procedures']:
            indication = Indication.query.filter_by(
                note_id=note.id,
                procedure_id=proc_id
            ).first()
            if indication:
                indication.performed = True
            else:
                indication = Indication(
                    note_id=note.id,
                    procedure_id=proc_id,
                    indicated=False,
                    performed=True
                )
                db.session.add(indication)
    
    db.session.commit()
    
    return jsonify({'success': True, 'note_id': note.id})

@app.route('/api/patient/<int:patient_id>/tags', methods=['POST'])
@login_required
def update_patient_tags(patient_id):
    data = request.json
    
    PatientTag.query.filter_by(patient_id=patient_id).delete()
    
    for tag_id in data['tags']:
        patient_tag = PatientTag(patient_id=patient_id, tag_id=tag_id)
        db.session.add(patient_tag)
    
    db.session.commit()
    
    return jsonify({'success': True})

@app.route('/chat')
@login_required
def chat():
    return render_template('chat.html')

@app.route('/api/chat/messages')
@login_required
def get_messages():
    messages = ChatMessage.query.order_by(ChatMessage.created_at.asc()).limit(100).all()
    
    return jsonify([{
        'id': msg.id,
        'sender': msg.sender.name,
        'senderId': msg.sender_id,
        'message': msg.message,
        'timestamp': msg.created_at.strftime('%H:%M'),
        'read': msg.read
    } for msg in messages])

@app.route('/api/chat/send', methods=['POST'])
@login_required
def send_message():
    data = request.json
    
    message = ChatMessage(
        sender_id=current_user.id,
        message=data['message']
    )
    
    db.session.add(message)
    db.session.commit()
    
    return jsonify({'success': True, 'id': message.id})

@app.route('/api/chat/mark_read', methods=['POST'])
@login_required
def mark_messages_read():
    ChatMessage.query.filter(
        ChatMessage.sender_id != current_user.id,
        ChatMessage.read == False
    ).update({'read': True})
    
    db.session.commit()
    
    return jsonify({'success': True})

@app.cli.command('init-db')
def init_db():
    """Inicializa o banco de dados com dados de demonstração."""
    with app.app_context():
        db.create_all()
        
        if User.query.count() == 0:
            doctor = User(
                email='arthur@clinicabasiledemo.com',
                name='Dr. Arthur Basile',
                role='medico'
            )
            doctor.set_password('123456')
            db.session.add(doctor)
            
            secretary = User(
                email='secretaria@clinicabasiledemo.com',
                name='Secretária',
                role='secretaria'
            )
            secretary.set_password('123456')
            db.session.add(secretary)
            
            procedures = [
                Procedure(name='Ulthera', description='Ultrassom microfocado'),
                Procedure(name='Morpheus8', description='Microagulhamento com radiofrequência'),
                Procedure(name='Sculptra', description='Bioestimulador de colágeno'),
                Procedure(name='Exilis', description='Radiofrequência'),
                Procedure(name='Neo', description='Tratamento combinado'),
                Procedure(name='Entone', description='Tonificação muscular')
            ]
            for proc in procedures:
                db.session.add(proc)
            
            tags = [
                Tag(name='Pré-operatório', color='#ffc107'),
                Tag(name='VIP', color='#6f42c1'),
                Tag(name='Potencial Sculptra', color='#20c997'),
                Tag(name='Retorno', color='#0dcaf0'),
                Tag(name='Primeira Consulta', color='#fd7e14')
            ]
            for tag in tags:
                db.session.add(tag)
            
            patient1 = Patient(
                name='Maria Silva',
                phone='(11) 98765-4321',
                email='maria@example.com'
            )
            db.session.add(patient1)
            
            patient2 = Patient(
                name='João Santos',
                phone='(11) 91234-5678',
                email='joao@example.com'
            )
            db.session.add(patient2)
            
            db.session.flush()
            
            today = get_brazil_time()
            apt1 = Appointment(
                patient_id=patient1.id,
                doctor_id=doctor.id,
                start_time=today.replace(hour=9, minute=0, second=0, microsecond=0),
                end_time=today.replace(hour=10, minute=0, second=0, microsecond=0),
                status='agendado',
                notes='Consulta de retorno'
            )
            db.session.add(apt1)
            
            apt2 = Appointment(
                patient_id=patient2.id,
                doctor_id=doctor.id,
                start_time=today.replace(hour=14, minute=0, second=0, microsecond=0),
                end_time=today.replace(hour=15, minute=0, second=0, microsecond=0),
                status='confirmado',
                notes='Primeira consulta'
            )
            db.session.add(apt2)
            
            db.session.commit()
            
            click.echo('Banco de dados inicializado com sucesso!')
            click.echo('Usuários criados:')
            click.echo('  Médico: arthur@clinicabasiledemo.com / 123456')
            click.echo('  Secretária: secretaria@clinicabasiledemo.com / 123456')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
