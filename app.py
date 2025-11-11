from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, send_file, make_response
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_wtf.csrf import CSRFProtect
from flask_mail import Mail
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta, date
import pytz
import click
from io import BytesIO

from config import Config
from models import db, User, Patient, Appointment, Note, Procedure, Indication, Tag, PatientTag, ChatMessage, CosmeticProcedurePlan, HairTransplant, TransplantImage, FollowUpReminder

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
csrf = CSRFProtect(app)
mail = Mail(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Por favor, faça login para acessar esta página.'

# Registrar Blueprints
from routes.surgical_map import surgical_map_bp
from routes.waiting_room import waiting_room_bp
from routes.settings import settings_bp

app.register_blueprint(surgical_map_bp)
app.register_blueprint(waiting_room_bp)
app.register_blueprint(settings_bp)

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
    """Retorna o ID do médico - se o usuário atual é médico, retorna seu ID"""
    if current_user.is_doctor():
        return current_user.id
    else:
        # Secretária: retorna None para permitir seleção de médico no frontend
        return None
        
def get_all_doctors():
    """Retorna todos os médicos com suas preferências de cor"""
    from models import DoctorPreference
    doctors = User.query.filter_by(role='medico').all()
    result = []
    for doctor in doctors:
        pref = DoctorPreference.query.filter_by(user_id=doctor.id).first()
        result.append({
            'id': doctor.id,
            'name': doctor.name,
            'color': pref.color if pref else '#0d6efd',
            'layer_enabled': pref.layer_enabled if pref else True
        })
    return result

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
        'agendados': sum(1 for a in appointments if a.status in ['agendado', 'confirmado']),
        'confirmados': sum(1 for a in appointments if a.status == 'confirmado'),
        'atendidos': sum(1 for a in appointments if a.status == 'atendido'),
        'faltaram': sum(1 for a in appointments if a.status == 'faltou')
    }
    
    return render_template('dashboard.html', stats=stats)

@app.route('/agenda')
@login_required
def agenda():
    doctors = get_all_doctors()
    return render_template('agenda.html', doctors=doctors)

@app.route('/api/appointments')
@login_required
def get_appointments():
    # Permitir filtrar por médico específico
    doctor_id = request.args.get('doctor_id', type=int)
    
    # Se não especificou e é médico, usa o próprio ID
    if not doctor_id and current_user.is_doctor():
        doctor_id = current_user.id
    
    # Se especificou médico, filtra. Senão retorna todos (para secretária ver todos os médicos)
    if doctor_id:
        appointments = Appointment.query.filter_by(doctor_id=doctor_id).all()
    else:
        appointments = Appointment.query.all()
    
    events = []
    for apt in appointments:
        # Get doctor color from DoctorPreference
        from models import DoctorPreference
        pref = DoctorPreference.query.filter_by(user_id=apt.doctor_id).first()
        doctor_color = pref.color if pref else '#0d6efd'
        
        # Use status color for border
        border_color = {
            'agendado': '#6c757d',
            'confirmado': '#0d6efd',
            'atendido': '#198754',
            'faltou': '#dc3545'
        }.get(apt.status, '#6c757d')
        
        events.append({
            'id': apt.id,
            'title': f"{apt.patient.name} - Dr. {apt.doctor.name}",
            'start': apt.start_time.isoformat(),
            'end': apt.end_time.isoformat(),
            'backgroundColor': doctor_color,
            'borderColor': border_color,
            'extendedProps': {
                'status': apt.status,
                'appointmentType': apt.appointment_type or 'Particular',
                'patientId': apt.patient_id,
                'doctorId': apt.doctor_id,
                'doctorName': apt.doctor.name,
                'waiting': apt.waiting,
                'checkedInTime': apt.checked_in_time.isoformat() if apt.checked_in_time else None,
                'phone': apt.patient.phone or '',
                'notes': apt.notes or ''
            }
        })
    
    return jsonify(events)

@app.route('/api/appointments', methods=['POST'])
@login_required
def create_appointment():
    data = request.json
    
    # Se secretária, doctor_id vem do payload. Se médico, usa próprio ID
    doctor_id = data.get('doctor_id') if not current_user.is_doctor() else get_doctor_id()
    
    if not doctor_id:
        return jsonify({'success': False, 'error': 'Médico não especificado'}), 400
    
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
        appointment_type=data.get('appointmentType', 'Particular'),
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

@app.route('/agenda/export/pdf', methods=['GET'])
@login_required
def export_agenda_pdf():
    """Exporta agenda em PDF"""
    from utils.exports.pdf_export import PDFExporter
    
    start_date = request.args.get('start', datetime.now().strftime('%Y-%m-%d'))
    end_date = request.args.get('end', datetime.now().strftime('%Y-%m-%d'))
    doctor_id_param = request.args.get('doctor_id', type=int)
    
    start = datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.strptime(end_date, '%Y-%m-%d')
    
    # Determine doctor - médico usa próprio ID, secretária pode especificar
    if current_user.is_doctor():
        doctor_id = current_user.id
    else:
        doctor_id = doctor_id_param
        if not doctor_id:
            return jsonify({'error': 'Especifique o médico'}), 400
    
    doctor = User.query.get(doctor_id)
    if not doctor:
        return jsonify({'error': 'Médico não encontrado'}), 404
    
    appointments = Appointment.query.filter(
        Appointment.doctor_id == doctor_id,
        Appointment.start_time >= start,
        Appointment.start_time <= end
    ).order_by(Appointment.start_time).all()
    
    exporter = PDFExporter()
    pdf_buffer = exporter.export_agenda(appointments, (start, end), doctor.name)
    
    return pdf_buffer.getvalue(), 200, {
        'Content-Type': 'application/pdf',
        'Content-Disposition': f'attachment; filename=agenda_{start_date}.pdf'
    }

@app.route('/agenda/export/excel', methods=['GET'])
@login_required
def export_agenda_excel():
    """Exporta agenda em Excel"""
    from utils.exports.excel_export import ExcelExporter
    
    start_date = request.args.get('start', datetime.now().strftime('%Y-%m-%d'))
    end_date = request.args.get('end', datetime.now().strftime('%Y-%m-%d'))
    doctor_id_param = request.args.get('doctor_id', type=int)
    
    start = datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.strptime(end_date, '%Y-%m-%d')
    
    # Determine doctor - médico usa próprio ID, secretária pode especificar
    if current_user.is_doctor():
        doctor_id = current_user.id
    else:
        doctor_id = doctor_id_param
        if not doctor_id:
            return jsonify({'error': 'Especifique o médico'}), 400
    
    doctor = User.query.get(doctor_id)
    if not doctor:
        return jsonify({'error': 'Médico não encontrado'}), 404
    
    appointments = Appointment.query.filter(
        Appointment.doctor_id == doctor_id,
        Appointment.start_time >= start,
        Appointment.start_time <= end
    ).order_by(Appointment.start_time).all()
    
    exporter = ExcelExporter()
    excel_buffer = exporter.export_agenda(appointments, (start, end), doctor.name)
    
    return excel_buffer.getvalue(), 200, {
        'Content-Type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'Content-Disposition': f'attachment; filename=agenda_{start_date}.xlsx'
    }

@app.route('/agenda/send-email', methods=['POST'])
@login_required
def send_agenda_email():
    """Envia agenda por email"""
    from utils.exports.pdf_export import PDFExporter
    from utils.exports.excel_export import ExcelExporter
    from services.email_service import EmailService
    
    data = request.json
    recipient = data.get('recipient')
    start_date = datetime.strptime(data.get('start_date'), '%Y-%m-%d')
    end_date = datetime.strptime(data.get('end_date'), '%Y-%m-%d')
    include_pdf = data.get('include_pdf', True)
    include_excel = data.get('include_excel', True)
    doctor_id_param = data.get('doctor_id')  # Safe parsing without type=int
    
    if not recipient:
        return jsonify({'error': 'Email do destinatário é obrigatório'}), 400
    
    # Determine doctor - médico usa próprio ID, secretária pode especificar
    if current_user.is_doctor():
        doctor_id = current_user.id
    else:
        doctor_id = doctor_id_param
        if not doctor_id:
            return jsonify({'error': 'Especifique o médico'}), 400
    
    doctor = User.query.get(doctor_id)
    if not doctor:
        return jsonify({'error': 'Médico não encontrado'}), 404
    
    appointments = Appointment.query.filter(
        Appointment.doctor_id == doctor_id,
        Appointment.start_time >= start_date,
        Appointment.start_time <= end_date
    ).order_by(Appointment.start_time).all()
    
    pdf_buffer = None
    excel_buffer = None
    
    if include_pdf:
        exporter = PDFExporter()
        pdf_buffer = exporter.export_agenda(appointments, (start_date, end_date), doctor.name)
    
    if include_excel:
        exporter = ExcelExporter()
        excel_buffer = exporter.export_agenda(appointments, (start_date, end_date), doctor.name)
    
    email_service = EmailService(mail)
    success = email_service.send_agenda_report(
        recipient,
        pdf_buffer=pdf_buffer,
        excel_buffer=excel_buffer,
        date_range=(start_date, end_date),
        doctor_name=doctor.name
    )
    
    if success:
        return jsonify({'success': True, 'message': 'Email enviado com sucesso'})
    else:
        return jsonify({'error': 'Erro ao enviar email'}), 500

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

@app.route('/api/prontuario/<int:patient_id>/cosmetic-plan', methods=['POST'])
@login_required
def save_cosmetic_plan(patient_id):
    """Salva planejamento cosmético com procedimentos e valores"""
    if not current_user.is_doctor():
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403
    
    from models import CosmeticProcedurePlan, FollowUpReminder
    from datetime import timedelta
    
    data = request.json
    
    # Criar nota principal
    note = Note(
        patient_id=patient_id,
        doctor_id=current_user.id,
        note_type='cosmiatria',
        category='cosmiatria',
        content=f"Anamnese: {data.get('anamnese', '')}\n\nConduta: {data.get('conduta', '')}"
    )
    db.session.add(note)
    db.session.flush()
    
    # Adicionar procedimentos ao planejamento
    for proc in data.get('procedures', []):
        plan = CosmeticProcedurePlan(
            note_id=note.id,
            procedure_name=proc['name'],
            planned_value=float(proc['value']),
            follow_up_months=int(proc['months'])
        )
        db.session.add(plan)
        
        # Criar lembrete automático de follow-up (usando timezone correto)
        follow_up_date = (get_brazil_time() + timedelta(days=30 * int(proc['months']))).date()
        reminder = FollowUpReminder(
            patient_id=patient_id,
            procedure_name=proc['name'],
            scheduled_date=follow_up_date,
            reminder_type='cosmetic_follow_up',
            notes=f"Retorno para {proc['name']}"
        )
        db.session.add(reminder)
    
    db.session.commit()
    return jsonify({'success': True})

@app.route('/api/prontuario/<int:patient_id>/generate-budget', methods=['POST'])
@login_required
def generate_budget_pdf(patient_id):
    """Gera orçamento PDF de procedimentos cosméticos"""
    if not current_user.is_doctor():
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403
    
    from utils.exports.budget_export import BudgetExporter
    
    data = request.json
    patient = Patient.query.get_or_404(patient_id)
    
    exporter = BudgetExporter()
    pdf_buffer = exporter.generate_budget(
        data.get('procedures', []),
        patient.name,
        current_user.name
    )
    
    return pdf_buffer.getvalue(), 200, {
        'Content-Type': 'application/pdf',
        'Content-Disposition': f'attachment; filename=orcamento_{patient_id}.pdf'
    }

@app.route('/api/prontuario/<int:patient_id>/hair-transplant', methods=['POST'])
@login_required
def save_hair_transplant(patient_id):
    """Salva dados de transplante capilar com uploads de imagens"""
    if not current_user.is_doctor():
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403
    
    from models import HairTransplant, TransplantImage, FollowUpReminder
    from werkzeug.utils import secure_filename
    import os
    import imghdr
    
    # Validação de upload de imagens
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
    
    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    
    def validate_image(file):
        """Valida se o arquivo é realmente uma imagem"""
        if not file:
            return False
        
        # Verificar extensão
        if not allowed_file(file.filename):
            return False
        
        # Verificar tamanho
        file.seek(0, os.SEEK_END)
        size = file.tell()
        file.seek(0)
        if size > MAX_FILE_SIZE:
            return False
        
        # Verificar MIME type lendo os primeiros bytes
        header = file.read(512)
        file.seek(0)
        file_type = imghdr.what(None, header)
        
        return file_type in ['jpeg', 'png', 'gif']
    
    # Criar nota principal
    note = Note(
        patient_id=patient_id,
        doctor_id=current_user.id,
        note_type='transplante_capilar',
        category='transplante_capilar',
        content=f"Queixa: {request.form.get('queixa', '')}\n\nConduta: {request.form.get('conduta', '')}"
    )
    db.session.add(note)
    db.session.flush()
    
    # Criar registro de transplante
    transplant = HairTransplant(
        note_id=note.id,
        norwood_classification=request.form.get('norwood'),
        case_type=request.form.get('case_type'),
        body_hair_needed=request.form.get('body_hair') == 'true',
        eyebrow_transplant=request.form.get('eyebrow_transplant') == 'true',
        beard_transplant=request.form.get('beard_transplant') == 'true',
        frontal_transplant=request.form.get('frontal') == 'true',
        crown_transplant=request.form.get('crown') == 'true',
        complete_transplant=request.form.get('complete') == 'true',
        complete_with_body_hair=request.form.get('complete_body_hair') == 'true',
        surgical_planning=request.form.get('surgical_planning', ''),
        clinical_conduct=request.form.get('conduta', '')
    )
    db.session.add(transplant)
    db.session.flush()
    
    # Upload de imagens (com validação rigorosa)
    upload_folder = 'uploads/transplant_images'  # Movido para fora de static/
    os.makedirs(upload_folder, exist_ok=True)
    
    image_types = [
        ('consultation_photo', 'consultation_photo'),
        ('surgical_plan', 'surgical_plan'),
        ('simulation', 'simulation')
    ]
    
    for field_name, image_type in image_types:
        if field_name in request.files:
            file = request.files[field_name]
            if file and file.filename:
                # Validar imagem
                if not validate_image(file):
                    db.session.rollback()
                    return jsonify({
                        'success': False, 
                        'error': f'Arquivo {file.filename} inválido. Apenas imagens JPG, PNG ou GIF até 5MB são permitidas.'
                    }), 400
                
                # Gerar nome seguro
                ext = file.filename.rsplit('.', 1)[1].lower()
                filename = secure_filename(f"{patient_id}_{image_type}_{int(get_brazil_time().timestamp())}.{ext}")
                filepath = os.path.join(upload_folder, filename)
                file.save(filepath)
                
                transplant_image = TransplantImage(
                    hair_transplant_id=transplant.id,
                    image_type=image_type,
                    file_path=filepath
                )
                db.session.add(transplant_image)
    
    # Criar lembretes de follow-up para transplante (usando timezone correto)
    reminders_schedule = [
        (7, 'Revisão pós-operatória 7 dias'),
        (180, 'Avaliação de crescimento 6 meses'),
        (365, 'Avaliação de resultado 12 meses')
    ]
    
    for days, notes in reminders_schedule:
        follow_up_date = (get_brazil_time() + timedelta(days=days)).date()
        reminder = FollowUpReminder(
            patient_id=patient_id,
            procedure_name='Transplante Capilar',
            scheduled_date=follow_up_date,
            reminder_type='transplant_revision',
            notes=notes
        )
        db.session.add(reminder)
    
    db.session.commit()
    return jsonify({'success': True})

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
