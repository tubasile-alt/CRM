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
from models import db, User, Patient, Appointment, Note, Procedure, Indication, Tag, PatientTag, ChatMessage, MessageRead, CosmeticProcedurePlan, HairTransplant, TransplantImage, FollowUpReminder, Payment

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
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({'success': False, 'error': 'Dados inválidos'}), 400
    
    # Se secretária, doctor_id vem do payload. Se médico, usa próprio ID
    doctor_id = data.get('doctor_id') if not current_user.is_doctor() else get_doctor_id()
    
    if not doctor_id:
        return jsonify({'success': False, 'error': 'Médico não especificado'}), 400
    
    patient = Patient.query.filter_by(name=data['patientName']).first()
    if not patient:
        patient = Patient(
            name=data['patientName'],
            phone=data.get('phone', ''),
            email=data.get('email', ''),
            patient_type=data.get('patientType', 'particular')
        )
        db.session.add(patient)
        db.session.flush()
    else:
        # Atualizar patient_type se fornecido
        if 'patientType' in data:
            patient.patient_type = data['patientType']
    
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
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({'success': False, 'error': 'Dados inválidos'}), 400
    
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
    
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({'error': 'Dados inválidos'}), 400
    
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

@app.route('/api/patient/<int:patient_id>/attention-note', methods=['POST'])
@login_required
def save_attention_note(patient_id):
    if not current_user.is_doctor():
        return jsonify({'success': False, 'error': 'Apenas médicos'}), 403
    
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'success': False, 'error': 'Dados inválidos'}), 400
    
    patient = Patient.query.get_or_404(patient_id)
    patient.attention_note = data.get('attention_note', '')
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
    
    # Carregar notas com todos os dados relacionados (eager loading)
    notes = Note.query.filter_by(patient_id=patient_id)\
        .options(
            db.joinedload(Note.indications).joinedload(Indication.procedure),
            db.joinedload(Note.cosmetic_plans),
            db.joinedload(Note.hair_transplants).joinedload(HairTransplant.images)
        )\
        .order_by(Note.created_at.desc())\
        .all()
    
    # Agrupar notas por consulta - PRIORIZAR appointment_id quando disponível
    from datetime import timedelta
    from collections import defaultdict
    
    consultations = []
    processed_notes = set()
    
    # Indexar notas por appointment_id (O(n))
    notes_by_appointment = defaultdict(list)
    notes_without_appointment = []
    
    for note in notes:
        if note.appointment_id:
            notes_by_appointment[note.appointment_id].append(note)
        else:
            notes_without_appointment.append(note)
    
    # Agrupar notas POR APPOINTMENT_ID (determinístico)
    for appt_id, appt_notes in notes_by_appointment.items():
        # Marcar como processadas
        for note in appt_notes:
            processed_notes.add(note.id)
        
        # Forçar carregamento de dados relacionados ENQUANTO a sessão está ativa
        all_cosmetic_plans = []
        for note in appt_notes:
            _ = note.cosmetic_plans
            _ = note.hair_transplants
            _ = note.indications
            # Extrair procedimentos cosméticos enquanto dados estão acessíveis
            for plan in note.cosmetic_plans:
                all_cosmetic_plans.append({
                    'procedure_name': plan.procedure_name,
                    'planned_value': plan.planned_value,
                    'final_budget': plan.final_budget,
                    'was_performed': plan.was_performed,
                    'performed_date': plan.performed_date,
                    'follow_up_months': plan.follow_up_months
                })
        
        # Separar notas por tipo
        notes_by_type = {note.note_type: note for note in appt_notes}
        
        # Identificar consulta finalizada (tem consultation_duration)
        finalized_note = next((n for n in appt_notes if n.consultation_duration), None)
        is_finalized = finalized_note is not None
        
        # Usar dados da primeira nota como referência
        first_note = sorted(appt_notes, key=lambda x: x.created_at)[0]
        
        consultations.append({
            'id': appt_id,  # Usar appointment_id como ID único
            'date': finalized_note.created_at if finalized_note else first_note.created_at,
            'doctor': first_note.doctor,
            'duration': finalized_note.consultation_duration if finalized_note else None,
            'category': finalized_note.category if finalized_note else first_note.category,
            'notes_by_type': notes_by_type,
            'all_notes': appt_notes,
            'cosmetic_plans': all_cosmetic_plans,
            'is_finalized': is_finalized
        })
    
    # FALLBACK: Agrupar notas SEM appointment_id usando janela de SEGUNDOS (mesma sessão)
    notes_without_appointment.sort(key=lambda x: x.created_at, reverse=True)
    
    for note in notes_without_appointment:
        if note.id in processed_notes:
            continue
        
        # Agrupar apenas notas criadas com menos de 2 segundos de diferença (mesma transação/sessão)
        window_start = note.created_at - timedelta(seconds=2)
        window_end = note.created_at + timedelta(seconds=2)
        
        grouped_notes = [n for n in notes_without_appointment
                        if n.id not in processed_notes
                        and n.doctor_id == note.doctor_id
                        and window_start <= n.created_at <= window_end]
        
        # Marcar como processadas
        for gn in grouped_notes:
            processed_notes.add(gn.id)
        
        # Forçar carregamento de dados relacionados ENQUANTO a sessão está ativa
        all_cosmetic_plans = []
        for gn in grouped_notes:
            _ = gn.cosmetic_plans
            _ = gn.hair_transplants
            _ = gn.indications
            # Extrair procedimentos cosméticos enquanto dados estão acessíveis
            for plan in gn.cosmetic_plans:
                all_cosmetic_plans.append({
                    'procedure_name': plan.procedure_name,
                    'planned_value': plan.planned_value,
                    'final_budget': plan.final_budget,
                    'was_performed': plan.was_performed,
                    'performed_date': plan.performed_date,
                    'follow_up_months': plan.follow_up_months
                })
        
        # Separar por tipo
        notes_by_type = {gn.note_type: gn for gn in grouped_notes}
        
        # Identificar se foi finalizada
        finalized_note = next((n for n in grouped_notes if n.consultation_duration), None)
        
        consultations.append({
            'id': note.id,
            'date': note.created_at,
            'doctor': note.doctor,
            'duration': finalized_note.consultation_duration if finalized_note else None,
            'category': note.category,
            'notes_by_type': notes_by_type,
            'all_notes': grouped_notes,
            'cosmetic_plans': all_cosmetic_plans,
            'is_finalized': finalized_note is not None
        })
    
    # Reordenar por data (mais recente primeiro)
    consultations.sort(key=lambda x: x['date'], reverse=True)
    
    # Pegar appointment_id da query string (opcional)
    appointment_id = request.args.get('appointment_id', type=int)
    
    return render_template('prontuario.html', 
                         patient=patient, 
                         procedures=procedures,
                         tags=tags,
                         patient_tags=patient_tags,
                         notes=notes,
                         consultations=consultations,
                         appointment_id=appointment_id)

@app.route('/api/prontuario/<int:patient_id>', methods=['POST'])
@login_required
def save_prontuario(patient_id):
    if not current_user.is_doctor():
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403
    
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({'success': False, 'error': 'Dados inválidos'}), 400
    
    note = Note(
        patient_id=patient_id,
        doctor_id=current_user.id,
        appointment_id=data.get('appointment_id'),  # Novo campo para agrupamento
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

@app.route('/api/prontuario/<int:patient_id>/finalizar', methods=['POST'])
@login_required
def finalizar_atendimento(patient_id):
    """Finaliza atendimento salvando todos os dados em uma transação unificada"""
    if not current_user.is_doctor():
        return jsonify({'success': False, 'error': 'Não autorizado'}), 403
    
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({'success': False, 'error': 'Dados inválidos'}), 400
    
    # Validar que o atendimento foi iniciado
    if not data.get('consultation_started'):
        return jsonify({'success': False, 'error': 'É necessário iniciar o atendimento antes de finalizar'}), 400
    
    try:
        category = data.get('category', 'patologia')
        duration = data.get('duration')
        appointment_id = data.get('appointment_id')  # Chave de agrupamento
        
        # Salvar cada seção como nota separada
        sections = ['queixa', 'anamnese', 'diagnostico']
        note_ids = {}
        
        for section in sections:
            content = data.get(section, '').strip()
            if content:  # Só salva se tiver conteúdo
                note = Note(
                    patient_id=patient_id,
                    doctor_id=current_user.id,
                    appointment_id=appointment_id,  # Agrupa consultas
                    note_type=section,
                    content=content,
                    category=category  # Adicionar categoria
                )
                db.session.add(note)
                db.session.flush()
                note_ids[section] = note.id
        
        # SEMPRE criar nota de conduta se houver dados estruturados ou texto
        conduta_content = data.get('conduta', '').strip()
        has_procedures = (data.get('indicated_procedures') or 
                         data.get('performed_procedures') or 
                         data.get('cosmetic_procedures') or 
                         data.get('transplant_data'))
        
        if conduta_content or has_procedures:
            conduta_note = Note(
                patient_id=patient_id,
                doctor_id=current_user.id,
                appointment_id=appointment_id,  # Agrupa consultas
                note_type='conduta',
                category=category,  # Adicionar categoria
                content=conduta_content or '[Conduta registrada via procedimentos]',
                consultation_duration=duration
            )
            db.session.add(conduta_note)
            db.session.flush()
            note_ids['conduta'] = conduta_note.id
        
        # Salvar procedimentos indicados e realizados (Patologia e Cosmiatria)
        if category != 'transplante_capilar':
            indicated = data.get('indicated_procedures', [])
            performed = data.get('performed_procedures', [])
            conduta_note_id = note_ids.get('conduta')
            
            if conduta_note_id:
                # Salvar procedimentos indicados
                for proc_id in indicated:
                    indication = Indication(
                        note_id=conduta_note_id,
                        procedure_id=proc_id,
                        indicated=True,
                        performed=(proc_id in performed)
                    )
                    db.session.add(indication)
                
                # Salvar procedimentos realizados que não foram indicados
                for proc_id in performed:
                    if proc_id not in indicated:
                        indication = Indication(
                            note_id=conduta_note_id,
                            procedure_id=proc_id,
                            indicated=False,
                            performed=True
                        )
                        db.session.add(indication)
        
        # Salvar planejamento cosmético (Cosmiatria)
        if category == 'cosmiatria':
            from models import CosmeticProcedurePlan, FollowUpReminder
            from datetime import timedelta
            
            procedures = data.get('cosmetic_procedures', [])
            conduta_note_id = note_ids.get('conduta')
            
            if conduta_note_id and procedures:
                # Sempre criar NOVOS registros para cada atendimento (mantém histórico)
                for proc in procedures:
                    proc_name = proc['name']
                    
                    # Criar novo plano para este atendimento
                    from datetime import datetime as dt
                    
                    # Processar data de realização se fornecida
                    performed_date_value = None
                    if proc.get('performedDate'):
                        try:
                            performed_date_value = dt.strptime(proc['performedDate'], '%Y-%m-%d').date()
                        except:
                            performed_date_value = None
                    
                    plan = CosmeticProcedurePlan(
                        note_id=conduta_note_id,
                        procedure_name=proc_name,
                        planned_value=float(proc['value']),
                        final_budget=float(proc.get('budget', proc['value'])),
                        was_performed=bool(proc.get('performed', False)),
                        performed_date=performed_date_value,
                        follow_up_months=int(proc['months'])
                    )
                    db.session.add(plan)
                    
                    # Gerenciar lembretes de follow-up
                    if proc.get('performed', False):
                        # Se foi realizado, cancelar lembretes pendentes anteriores
                        FollowUpReminder.query.filter_by(
                            patient_id=patient_id,
                            procedure_name=proc_name,
                            reminder_type='cosmetic_follow_up',
                            status='pending'
                        ).update({'status': 'completed'})
                    else:
                        # Se não foi realizado, criar novo lembrete e cancelar pendentes anteriores
                        # Primeiro cancela lembretes antigos
                        FollowUpReminder.query.filter_by(
                            patient_id=patient_id,
                            procedure_name=proc_name,
                            reminder_type='cosmetic_follow_up',
                            status='pending'
                        ).update({'status': 'superseded'})
                        
                        # Criar novo lembrete
                        follow_up_date = (get_brazil_time() + timedelta(days=30 * int(proc['months']))).date()
                        reminder = FollowUpReminder(
                            patient_id=patient_id,
                            procedure_name=proc_name,
                            scheduled_date=follow_up_date,
                            reminder_type='cosmetic_follow_up'
                        )
                        db.session.add(reminder)
            
            # CRIAR CHECKOUT AUTOMATICAMENTE para procedimentos realizados
            checkout_amount = data.get('checkout_amount', 0)
            checkout_procedures = data.get('checkout_procedures', [])
            consultation_type = data.get('consultation_type', 'Particular')  # Get from data
            
            if checkout_procedures:  # Se tem procedimentos, criar checkout
                # Adicionar valor da consulta conforme tipo
                procedures_list = [{
                    'name': proc.get('name', 'Procedimento'),
                    'value': float(proc.get('budget', proc.get('value', 0)))
                } for proc in checkout_procedures]
                
                # Adicionar consulta base se for Particular ou Implante Capilar
                total_amount = checkout_amount
                if consultation_type in ['Particular', 'Implante Capilar']:
                    consultation_fee = CONSULTATION_PRICES.get(consultation_type, 0.0)
                    if consultation_fee > 0:
                        procedures_list.insert(0, {
                            'name': f'Consulta {consultation_type}',
                            'value': consultation_fee
                        })
                        total_amount += consultation_fee
                
                payment = Payment(
                    appointment_id=appointment_id,  # Pode ser None
                    patient_id=patient_id,
                    total_amount=float(total_amount),
                    consultation_type=consultation_type,
                    payment_method='pendente',
                    status='pendente',
                    procedures=procedures_list
                )
                db.session.add(payment)
                print(f"✓✓✓ PAYMENT CRIADO: R${total_amount} - {consultation_type} - Paciente {patient_id} - Procedures: {len(procedures_list)}")
        
        # Salvar dados de transplante capilar (Transplante Capilar)
        if category == 'transplante_capilar':
            from models import HairTransplant
            
            transplant_data = data.get('transplant_data', {})
            conduta_note_id = note_ids.get('conduta')
            
            if conduta_note_id and transplant_data:
                transplant = HairTransplant(
                    note_id=conduta_note_id,
                    norwood_classification=transplant_data.get('norwood'),
                    previous_transplant=transplant_data.get('previous_transplant', 'nao'),
                    transplant_location=transplant_data.get('transplant_location'),
                    frontal_transplant=transplant_data.get('frontal', False),
                    crown_transplant=transplant_data.get('crown', False),
                    complete_transplant=transplant_data.get('complete', False),
                    complete_with_body_hair=transplant_data.get('complete_body_hair', False),
                    surgical_planning=transplant_data.get('surgical_planning', ''),
                    clinical_conduct=data.get('conduta', '')
                )
                db.session.add(transplant)
        
        # Atualizar status do agendamento para "atendido"
        appointment_id = data.get('appointment_id')
        if appointment_id:
            appointment = Appointment.query.filter_by(
                id=appointment_id,
                patient_id=patient_id,
                doctor_id=current_user.id
            ).first()
            
            if appointment:
                appointment.status = 'atendido'
                if not appointment.checked_in_time:
                    appointment.checked_in_time = get_brazil_time()
            else:
                print(f"Warning: Appointment {appointment_id} not found or not owned by current doctor")
        
        # Commit da transação
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Atendimento finalizado com sucesso',
            'note_ids': note_ids
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'Erro ao finalizar atendimento: {str(e)}'
        }), 500

@app.route('/api/prontuario/<int:patient_id>/cosmetic-plan', methods=['POST'])
@login_required
def save_cosmetic_plan(patient_id):
    """
    DEPRECATED: Não salva mais no banco - dados são salvos apenas ao finalizar atendimento.
    Mantido apenas para compatibilidade, retorna sucesso sem fazer nada.
    Use generate-budget para gerar PDF.
    """
    if not current_user.is_doctor():
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403
    
    # Não salvar mais - apenas retornar sucesso
    # Os dados serão salvos quando clicar em "Finalizar Atendimento"
    return jsonify({
        'success': True, 
        'message': 'Planejamento será salvo ao finalizar o atendimento'
    })

@app.route('/api/prontuario/<int:patient_id>/generate-budget', methods=['POST'])
@login_required
def generate_budget_pdf(patient_id):
    """Gera orçamento PDF de procedimentos cosméticos"""
    if not current_user.is_doctor():
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403
    
    from utils.exports.budget_export import BudgetExporter
    
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({'success': False, 'error': 'Dados inválidos'}), 400
    
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
        previous_transplant=request.form.get('previous_transplant', 'nao'),
        transplant_location=request.form.get('transplant_location'),
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
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({'success': False, 'error': 'Dados inválidos'}), 400
    
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
    with_user_id = request.args.get('with_user_id', type=int)
    
    if not with_user_id:
        return jsonify({'error': 'Parâmetro with_user_id é obrigatório'}), 400
    
    messages = ChatMessage.query.filter(
        db.or_(
            db.and_(
                ChatMessage.sender_id == current_user.id,
                ChatMessage.recipient_id == with_user_id
            ),
            db.and_(
                ChatMessage.sender_id == with_user_id,
                ChatMessage.recipient_id == current_user.id
            )
        )
    ).order_by(ChatMessage.created_at.asc()).limit(100).all()
    
    return jsonify([{
        'id': msg.id,
        'sender': msg.sender.name,
        'senderId': msg.sender_id,
        'recipient': msg.recipient.name,
        'recipientId': msg.recipient_id,
        'message': msg.message,
        'timestamp': msg.created_at.strftime('%H:%M'),
        'read': msg.read
    } for msg in messages])

@app.route('/api/chat/send', methods=['POST'])
@login_required
def send_message():
    data = request.get_json(silent=True) or request.form
    
    recipient_id = data.get('recipient_id')
    if not recipient_id:
        return jsonify({'error': 'recipient_id é obrigatório'}), 400
    
    recipient = User.query.get(int(recipient_id))
    if not recipient:
        return jsonify({'error': 'Destinatário não encontrado'}), 404
    
    message = ChatMessage(
        sender_id=current_user.id,
        recipient_id=int(recipient_id),
        message=data.get('message', '')
    )
    
    db.session.add(message)
    db.session.commit()
    
    return jsonify({'success': True, 'id': message.id})

@app.route('/api/chat/mark_read', methods=['POST'])
@login_required
def mark_messages_read():
    data = request.get_json(silent=True) or request.form
    from_user_id = data.get('from_user_id')
    if from_user_id:
        from_user_id = int(from_user_id)
    
    query = db.session.query(ChatMessage.id).filter(
        ChatMessage.recipient_id == current_user.id
    )
    
    if from_user_id:
        query = query.filter(ChatMessage.sender_id == from_user_id)
    
    unread_message_ids = query.outerjoin(
        MessageRead,
        db.and_(
            MessageRead.message_id == ChatMessage.id,
            MessageRead.user_id == current_user.id
        )
    ).filter(
        MessageRead.id.is_(None)
    ).all()
    
    if not unread_message_ids:
        return jsonify({'success': True, 'count': 0})
    
    read_records = [
        MessageRead(
            message_id=msg_id[0],
            user_id=current_user.id
        )
        for msg_id in unread_message_ids
    ]
    
    try:
        db.session.bulk_save_objects(read_records)
        db.session.commit()
        return jsonify({'success': True, 'count': len(read_records)})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/chat/unread_count')
@login_required
def get_unread_count():
    from_user_id = request.args.get('from_user_id', type=int)
    
    query = db.session.query(ChatMessage).filter(
        ChatMessage.recipient_id == current_user.id
    )
    
    if from_user_id:
        query = query.filter(ChatMessage.sender_id == from_user_id)
    
    count = query.outerjoin(
        MessageRead,
        db.and_(
            MessageRead.message_id == ChatMessage.id,
            MessageRead.user_id == current_user.id
        )
    ).filter(
        MessageRead.id.is_(None)
    ).count()
    
    return jsonify({'count': count})

@app.route('/api/chat/contacts')
@login_required
def get_chat_contacts():
    users = User.query.filter(User.id != current_user.id).all()
    
    contacts = []
    for user in users:
        unread_count = db.session.query(ChatMessage).filter(
            ChatMessage.recipient_id == current_user.id,
            ChatMessage.sender_id == user.id
        ).outerjoin(
            MessageRead,
            db.and_(
                MessageRead.message_id == ChatMessage.id,
                MessageRead.user_id == current_user.id
            )
        ).filter(
            MessageRead.id.is_(None)
        ).count()
        
        contacts.append({
            'id': user.id,
            'name': user.name,
            'role': user.role,
            'unread_count': unread_count
        })
    
    return jsonify(contacts)

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

@app.route('/api/prontuario/<int:patient_id>/cosmetic-plans', methods=['GET'])
@login_required
def get_cosmetic_plans(patient_id):
    """Retorna todos os planos cosméticos de um paciente"""
    if not current_user.is_doctor() and not current_user.is_secretary():
        return jsonify({'success': False, 'error': 'Não autorizado'}), 403
    
    from models import CosmeticProcedurePlan, Note
    
    plans = db.session.query(CosmeticProcedurePlan).join(Note).filter(
        Note.patient_id == patient_id
    ).order_by(CosmeticProcedurePlan.id.desc()).all()
    
    plans_data = []
    for plan in plans:
        plans_data.append({
            'id': plan.id,
            'procedure_name': plan.procedure_name,
            'planned_value': plan.planned_value,
            'final_budget': plan.final_budget,
            'was_performed': plan.was_performed,
            'performed_date': plan.performed_date.isoformat() if plan.performed_date else None,
            'follow_up_months': plan.follow_up_months,
            'created_at': plan.note.created_at.isoformat() if plan.note else None
        })
    
    return jsonify({'success': True, 'plans': plans_data})

@app.route('/api/prontuario/<int:patient_id>/cosmetic-plans-grouped', methods=['GET'])
@login_required
def get_cosmetic_plans_grouped(patient_id):
    """Retorna planos cosméticos agrupados por data de consulta"""
    if not current_user.is_doctor() and not current_user.is_secretary():
        return jsonify({'success': False, 'error': 'Não autorizado'}), 403
    
    from models import CosmeticProcedurePlan, Note, Appointment
    from collections import defaultdict
    
    plans = db.session.query(CosmeticProcedurePlan, Note).join(
        Note, CosmeticProcedurePlan.note_id == Note.id
    ).filter(
        Note.patient_id == patient_id
    ).order_by(Note.created_at.desc()).all()
    
    grouped_plans = defaultdict(list)
    consultation_info = {}
    
    for plan, note in plans:
        consultation_key = note.appointment_id if note.appointment_id else f"note_{note.id}"
        
        if consultation_key not in consultation_info:
            appointment = None
            if note.appointment_id:
                appointment = Appointment.query.get(note.appointment_id)
            
            consultation_info[consultation_key] = {
                'date': note.created_at.isoformat(),
                'appointment_id': note.appointment_id,
                'doctor_name': note.doctor.name if note.doctor else 'Desconhecido',
                'display_date': note.created_at.strftime('%d/%m/%Y %H:%M')
            }
        
        grouped_plans[consultation_key].append({
            'id': plan.id,
            'procedure_name': plan.procedure_name,
            'planned_value': float(plan.planned_value) if plan.planned_value else 0,
            'final_budget': float(plan.final_budget) if plan.final_budget else 0,
            'was_performed': plan.was_performed,
            'performed_date': plan.performed_date.isoformat() if plan.performed_date else None,
            'follow_up_months': plan.follow_up_months,
            'created_at': plan.created_at.isoformat() if plan.created_at else None
        })
    
    result = []
    for consultation_key, procedures in grouped_plans.items():
        result.append({
            'consultation_key': consultation_key,
            'consultation_info': consultation_info[consultation_key],
            'procedures': procedures
        })
    
    result.sort(key=lambda x: x['consultation_info']['date'], reverse=True)
    
    return jsonify({'success': True, 'grouped_plans': result})

@app.route('/api/prontuario/cosmetic-plan/<int:plan_id>', methods=['PATCH'])
@login_required
def update_cosmetic_plan(plan_id):
    """Atualiza um plano cosmético existente"""
    if not current_user.is_doctor():
        return jsonify({'success': False, 'error': 'Não autorizado'}), 403
    
    from models import CosmeticProcedurePlan
    
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({'success': False, 'error': 'Dados inválidos'}), 400
    
    plan = CosmeticProcedurePlan.query.get_or_404(plan_id)
    
    if 'planned_value' in data:
        plan.planned_value = float(data['planned_value'])
    if 'final_budget' in data:
        plan.final_budget = float(data['final_budget'])
    if 'was_performed' in data:
        plan.was_performed = bool(data['was_performed'])
        if plan.was_performed and not plan.performed_date:
            plan.performed_date = get_brazil_time().date()
    if 'follow_up_months' in data:
        plan.follow_up_months = int(data['follow_up_months'])
    
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Plano atualizado com sucesso'})

# CHECKOUT ROUTES
CONSULTATION_PRICES = {
    'Particular': 400.0,
    'Unimed': 0.0,
    'Retorno': 0.0,
    'Transplante Capilar': 400.0,
    'Cortesia': 0.0,
    'Consulta Cortesia': 0.0
}

@app.route('/api/checkout/pending', methods=['GET'])
@login_required
def get_pending_checkouts():
    if not current_user.is_secretary():
        return jsonify({'success': False, 'error': 'Apenas secretárias'}), 403
    
    today = get_brazil_time().date()
    
    # Buscar TODOS os checkouts do dia (pendentes E pagos)
    payments = Payment.query.filter(
        db.func.date(Payment.created_at) == today
    ).all()
    
    print(f"DEBUG: Found {len(payments)} payments for today")
    
    data = []
    for payment in payments:
        patient = payment.patient
        apt_id = payment.appointment_id if payment.appointment_id else 'N/A'
        data.append({
            'id': payment.id,
            'appointment_id': apt_id,
            'patient_name': patient.name if patient else 'Desconhecido',
            'consultation_type': payment.consultation_type,
            'total_amount': float(payment.total_amount),
            'procedures': payment.procedures or [],
            'created_at': payment.created_at.strftime('%H:%M'),
            'status': payment.status,
            'paid_at': payment.paid_at.strftime('%H:%M') if payment.paid_at else None,
            'payment_method': payment.payment_method
        })
        print(f"  - Payment {payment.id}: {patient.name if patient else '?'} R${payment.total_amount} - {payment.status}")
    
    return jsonify({'success': True, 'checkouts': data})

@app.route('/api/checkout/create', methods=['POST'])
@login_required
def create_checkout():
    if not current_user.is_doctor() and not current_user.is_secretary():
        return jsonify({'success': False, 'error': 'Não autorizado'}), 403
    
    data = request.get_json(silent=True)
    if not data or 'appointment_id' not in data:
        return jsonify({'success': False, 'error': 'Dados inválidos'}), 400
    
    appointment = Appointment.query.get(data['appointment_id'])
    if not appointment:
        return jsonify({'success': False, 'error': 'Consulta não encontrada'}), 404
    
    consultation_type = data.get('consultation_type', appointment.appointment_type or 'Particular')
    amount = CONSULTATION_PRICES.get(consultation_type, 0.0)
    
    payment = Payment(
        appointment_id=appointment.id,
        patient_id=appointment.patient_id,
        total_amount=amount,
        consultation_type=consultation_type,
        payment_method='pendente',
        procedures=data.get('procedures', [])
    )
    
    db.session.add(payment)
    db.session.commit()
    
    return jsonify({'success': True, 'payment_id': payment.id})

@app.route('/api/checkout/<int:payment_id>/pay', methods=['POST'])
@login_required
def process_payment(payment_id):
    if not current_user.is_secretary():
        return jsonify({'success': False, 'error': 'Apenas secretárias'}), 403
    
    data = request.get_json(silent=True)
    if not data or 'payment_method' not in data:
        return jsonify({'success': False, 'error': 'Método de pagamento obrigatório'}), 400
    
    payment = Payment.query.get(payment_id)
    if not payment:
        return jsonify({'success': False, 'error': 'Pagamento não encontrado'}), 404
    
    payment.payment_method = data['payment_method']
    payment.installments = data.get('installments', 1)
    payment.status = 'pago'
    payment.paid_at = get_brazil_time()
    
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Pagamento registrado com sucesso!'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
