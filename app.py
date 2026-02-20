from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, send_file, make_response
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_wtf.csrf import CSRFProtect
from flask_mail import Mail
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta, date
import pytz
import click
import os
from io import BytesIO

from config import Config
from models import db, User, Patient, Appointment, Note, Procedure, Indication, Tag, PatientTag, ChatMessage, MessageRead, CosmeticProcedurePlan, HairTransplant, TransplantImage, FollowUpReminder, Payment, PatientDoctor, Evolution, Surgery, OperatingRoom, Prescription
from utils.database_backup import backup_manager

app = Flask(__name__)
app.config.from_object(Config)

# Fazer backup automático ao iniciar a aplicação (DESABILITADO EM PRODUÇÃO)
# Este backup é executado apenas manualmente via init_backup.py
# @app.before_request
# def auto_backup():
#     """Fazer backup automático a cada 30 minutos"""
#     import time
#     cache_key = 'last_backup_time'
#     now = time.time()
#     
#     # Verificar se já fez backup recentemente (a cada 30 min = 1800 seg)
#     last_backup = app.config.get(cache_key, 0)
#     if (now - last_backup) > 1800:
#         try:
#             backup_manager.backup_sqlite()
#             app.config[cache_key] = now
#         except:
#             pass  # Não interromper requisição se backup falhar

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
from routes.patient import patient_bp
from routes.crm import crm_bp
from routes.dermascribe import dermascribe_bp

app.register_blueprint(surgical_map_bp)
app.register_blueprint(waiting_room_bp)
app.register_blueprint(settings_bp)
app.register_blueprint(crm_bp)
app.register_blueprint(dermascribe_bp)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))
app.register_blueprint(patient_bp)

def get_brazil_time():
    tz = pytz.timezone('America/Sao_Paulo')
    return datetime.now(tz)

def parse_datetime_with_tz(iso_string):
    """Parse ISO datetime string - retorna naive datetime para São Paulo.
    NÃO usamos timezone para evitar conversões automáticas do SQLAlchemy."""
    # Remove 'Z' suffix if present and parse
    iso_string = iso_string.replace('Z', '')
    dt = datetime.fromisoformat(iso_string)
    
    # Sempre retorna naive (sem timezone) - representa horário de São Paulo
    if dt.tzinfo is not None:
        # Se veio com timezone, converter para São Paulo e remover tzinfo
        tz = pytz.timezone('America/Sao_Paulo')
        dt = dt.astimezone(tz).replace(tzinfo=None)
    
    return dt

def format_brazil_datetime(dt):
    """Converte datetime para timezone de São Paulo e formata"""
    if not dt:
        return None
    tz = pytz.timezone('America/Sao_Paulo')
    
    # Se o datetime é naive (sem timezone), assume que já está em São Paulo
    if dt.tzinfo is None:
        dt = tz.localize(dt)
    else:
        # Se tem timezone, converte para São Paulo
        dt = dt.astimezone(tz)
    
    return dt.strftime('%d/%m/%Y %H:%M')

@app.route('/health')
def health():
    """Lightweight health check endpoint for deployment"""
    return jsonify({'status': 'ok'}), 200

@app.route('/api/dashboard/surgery-stats', methods=['GET'])
@login_required  
def get_surgery_stats():
    """Estatisticas de evolucoes cirurgicas para o dashboard"""
    from models import SurgeryEvolution, TransplantSurgeryRecord
    from sqlalchemy import func, extract
    from datetime import datetime
    import pytz
    
    evolutions_7days = SurgeryEvolution.query.filter_by(evolution_type='7_days').all()
    evolutions_1year = SurgeryEvolution.query.filter_by(evolution_type='1_year').all()
    
    # Estatisticas por tipo de cirurgia
    all_surgeries = TransplantSurgeryRecord.query.all()
    type_counts = {
        'Capilar': 0,
        'Body Hair': 0,
        'Sobrancelhas': 0,
        'Barba': 0,
        'Retoque': 0,
        'Outros': 0
    }
    for s in all_surgeries:
        if s.surgery_type:
            types = [t.strip() for t in s.surgery_type.split(',')]
            for t in types:
                if t in type_counts:
                    type_counts[t] += 1
                elif t:
                    type_counts['Outros'] += 1
    
    # Estatisticas por mes (ultimos 12 meses)
    tz = pytz.timezone('America/Sao_Paulo')
    now = datetime.now(tz)
    monthly_stats = []
    for i in range(12):
        month = now.month - i
        year = now.year
        if month <= 0:
            month += 12
            year -= 1
        count = TransplantSurgeryRecord.query.filter(
            extract('month', TransplantSurgeryRecord.surgery_date) == month,
            extract('year', TransplantSurgeryRecord.surgery_date) == year
        ).count()
        monthly_stats.append({
            'month': f'{month:02d}/{year}',
            'count': count
        })
    monthly_stats.reverse()
    
    stats = {
        'seven_day_stats': {
            'total': len(evolutions_7days),
            'necrosis': sum(1 for e in evolutions_7days if e.has_necrosis),
            'scabs': sum(1 for e in evolutions_7days if e.has_scabs),
            'infections': sum(1 for e in evolutions_7days if e.has_infection),
            'follicle_loss': sum(1 for e in evolutions_7days if e.has_follicle_loss)
        },
        'one_year_stats': {
            'total': len(evolutions_1year),
            'results': {
                'otimo': sum(1 for e in evolutions_1year if e.result_rating == 'otimo'),
                'bom': sum(1 for e in evolutions_1year if e.result_rating == 'bom'),
                'medio': sum(1 for e in evolutions_1year if e.result_rating == 'medio'),
                'ruim': sum(1 for e in evolutions_1year if e.result_rating == 'ruim')
            },
            'needs_another_surgery': sum(1 for e in evolutions_1year if e.needs_another_surgery)
        },
        'surgery_types': type_counts,
        'total_surgeries': len(all_surgeries),
        'monthly_stats': monthly_stats
    }
    
    return jsonify(stats)

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
    
    from datetime import timedelta
    
    today = get_brazil_time().date()
    
    # Hoje
    today_appointments = Appointment.query.filter(
        db.func.date(Appointment.start_time) == today,
        Appointment.doctor_id == current_user.id
    ).all()
    
    # Esta semana (segunda a domingo)
    monday = today - timedelta(days=today.weekday())
    sunday = monday + timedelta(days=6)
    week_appointments = Appointment.query.filter(
        Appointment.doctor_id == current_user.id,
        Appointment.start_time >= datetime.combine(monday, datetime.min.time()),
        Appointment.start_time <= datetime.combine(sunday, datetime.max.time())
    ).all()
    
    # Este mês
    first_day = today.replace(day=1)
    if today.month == 12:
        last_day = first_day.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
    else:
        last_day = first_day.replace(month=today.month + 1, day=1) - timedelta(days=1)
    
    month_appointments = Appointment.query.filter(
        Appointment.doctor_id == current_user.id,
        Appointment.start_time >= datetime.combine(first_day, datetime.min.time()),
        Appointment.start_time <= datetime.combine(last_day, datetime.max.time())
    ).all()
    
    # Carregar procedimentos do médico
    from models import Indication, CosmeticProcedurePlan, HairTransplant, Procedure
    from collections import defaultdict
    
    # Buscar todas as indicações do médico
    notes = Note.query.filter_by(doctor_id=current_user.id).all()
    note_ids = [n.id for n in notes]
    
    procedures_completed = defaultdict(int)
    procedures_pending = defaultdict(int)
    
    # Contar indicações feitas vs planejadas
    if note_ids:
        indications = Indication.query.filter(Indication.note_id.in_(note_ids)).all()
        for ind in indications:
            proc_name = ind.procedure.name if ind.procedure else 'Procedimento'
            if ind.performed:
                procedures_completed[proc_name] += 1
            elif ind.indicated:
                procedures_pending[proc_name] += 1
    
    # Contar planos cosméticos
    cosmetic_plans = CosmeticProcedurePlan.query.filter(CosmeticProcedurePlan.note_id.in_(note_ids)).all() if note_ids else []
    for plan in cosmetic_plans:
        proc_name = plan.procedure_name or 'Cosmético'
        if plan.was_performed:
            procedures_completed[proc_name] += 1
        else:
            procedures_pending[proc_name] += 1
    
    # Dados de procedimentos por mês (últimos 6 meses)
    procedures_by_month = defaultdict(lambda: {'completed': 0, 'pending': 0})
    
    if note_ids:
        # Últimos 6 meses
        for i in range(6):
            month_date = today - timedelta(days=30*i)
            month_key = month_date.strftime('%b %Y')
            procedures_by_month[month_key] = {'completed': 0, 'pending': 0}
        
        # Contar indicações por mês
        indications = Indication.query.filter(Indication.note_id.in_(note_ids)).all()
        for ind in indications:
            note = db.session.get(Note, ind.note_id)
            if note:
                month_key = note.created_at.strftime('%b %Y')
                if month_key in procedures_by_month:
                    if ind.performed:
                        procedures_by_month[month_key]['completed'] += 1
                    elif ind.indicated:
                        procedures_by_month[month_key]['pending'] += 1
        
        # Contar planos cosméticos por mês
        for plan in cosmetic_plans:
            note = db.session.get(Note, plan.note_id)
            if note:
                month_key = note.created_at.strftime('%b %Y')
                if month_key in procedures_by_month:
                    if plan.was_performed:
                        procedures_by_month[month_key]['completed'] += 1
                    else:
                        procedures_by_month[month_key]['pending'] += 1
    
    # Ordenar por data
    import json
    months_list = sorted(procedures_by_month.keys(), reverse=True)[:6]
    procedures_by_month_ordered = {m: procedures_by_month[m] for m in reversed(months_list)}
    
    stats = {
        'agendados': sum(1 for a in today_appointments if a.status in ['agendado', 'confirmado']),
        'confirmados': sum(1 for a in today_appointments if a.status == 'confirmado'),
        'atendidos': sum(1 for a in today_appointments if a.status == 'atendido'),
        'faltaram': sum(1 for a in today_appointments if a.status == 'faltou'),
        # Por semana
        'unimed_week': sum(1 for a in week_appointments if a.appointment_type == 'UNIMED'),
        'particular_week': sum(1 for a in week_appointments if a.appointment_type == 'Particular'),
        'transplante_week': sum(1 for a in week_appointments if a.appointment_type == 'Transplante Capilar'),
        # Por mês
        'unimed_month': sum(1 for a in month_appointments if a.appointment_type == 'UNIMED'),
        'particular_month': sum(1 for a in month_appointments if a.appointment_type == 'Particular'),
        'transplante_month': sum(1 for a in month_appointments if a.appointment_type == 'Transplante Capilar'),
        # Procedimentos
        'procedures_completed': dict(procedures_completed),
        'procedures_pending': dict(procedures_pending),
        'procedures_by_month': procedures_by_month_ordered,
        'procedures_by_month_json': json.dumps(procedures_by_month_ordered),
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
    from datetime import timedelta
    
    # Permitir filtrar por médico específico
    doctor_id = request.args.get('doctor_id', type=int)
    
    # Se não especificou e é médico, usa o próprio ID
    if not doctor_id and current_user.is_doctor():
        doctor_id = current_user.id
    
    # Filtrar por data específica (opcional mas recomendado para performance)
    date_str = request.args.get('date')
    
    # Base query
    query = Appointment.query
    
    if doctor_id:
        query = query.filter(Appointment.doctor_id == doctor_id)
    
    # Se data especificada, filtra apenas o dia selecionado (muito mais rápido)
    if date_str:
        try:
            from datetime import datetime
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            # Filtrar agendamentos do dia específico
            query = query.filter(
                db.func.date(Appointment.start_time) == target_date
            )
        except ValueError:
            pass  # Se data inválida, ignora o filtro
    
    appointments = query.all()
    
    # BUSCAR CIRURGIAS DO MAPA CIRÚRGICO PARA ESTE DIA
    from models import Surgery
    surgery_query = Surgery.query
    if date_str:
        try:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            surgery_query = surgery_query.filter(Surgery.date == target_date)
            if doctor_id:
                surgery_query = surgery_query.filter(Surgery.doctor_id == doctor_id)
        except:
            pass
    
    surgeries = surgery_query.all()
    
    events = []
    
    # ADICIONAR CIRURGIAS COMO EVENTOS NA AGENDA
    for surg in surgeries:
        try:
            # Timezone offset -03:00
            surg_start_dt = datetime.combine(surg.date, surg.start_time)
            surg_end_dt = datetime.combine(surg.date, surg.end_time)
            start_iso = surg_start_dt.isoformat() + '-03:00'
            end_iso = surg_end_dt.isoformat() + '-03:00'
            
            events.append({
                'id': f"surg_{surg.id}",
                'title': f"{surg.patient_name} - {surg.procedure_name}",
                'start': start_iso,
                'end': end_iso,
                'backgroundColor': '#dc3545', # Cor de cirurgia
                'borderColor': '#842029',
                'extendedProps': {
                    'status': surg.status or 'agendado',
                    'appointmentType': 'Cirurgia',
                    'patientName': surg.patient_name,
                    'doctorId': surg.doctor_id,
                    'doctorName': surg.doctor.name if surg.doctor else 'Dr. Arthur',
                    'notes': surg.notes or '',
                    'isSurgeryMap': True,
                    'patientId': None # Cirurgias do mapa podem não ter patient_id vinculado ainda
                }
            })
        except Exception as e:
            print(f"Erro ao processar cirurgia {surg.id} para agenda: {e}")

    for apt in appointments:
        try:
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
            
            # TIMEZONE: Banco armazena horários naive em São Paulo (sem conversão)
            # Retornar com offset timezone correto (-03:00) para evitar conversão UTC
            start_iso = apt.start_time.isoformat() + '-03:00' if apt.start_time else None
            end_iso = apt.end_time.isoformat() + '-03:00' if apt.end_time else None
            
            # Buscar código do paciente para este médico
            from models import PatientDoctor
            pd = PatientDoctor.query.filter_by(patient_id=apt.patient_id, doctor_id=apt.doctor_id).first()
            patient_code = pd.patient_code if pd else None
            
            # Buscar dados do paciente e médico com fallback em caso de erro
            patient_name = 'Paciente'
            patient_type = 'Particular'
            patient_phone = ''
            try:
                patient_name = apt.patient.name or 'Paciente'
                patient_type = apt.patient.patient_type or 'Particular'
                patient_phone = apt.patient.phone or ''
            except Exception as e:
                print(f"Erro ao carregar dados do paciente {apt.patient_id}: {e}")
            
            doctor_name = 'Dr. Desconhecido'
            try:
                doctor_name = f"Dr. {apt.doctor.name}" if apt.doctor else 'Dr. Desconhecido'
            except Exception as e:
                print(f"Erro ao carregar dados do médico {apt.doctor_id}: {e}")
            
            events.append({
                'id': apt.id,
                'title': f"{patient_name} - {doctor_name}",
                'start': start_iso,
                'end': end_iso,
                'backgroundColor': doctor_color,
                'borderColor': border_color,
                'extendedProps': {
                    'status': apt.status,
                    'appointmentType': apt.appointment_type or 'Particular',
                    'patientId': apt.patient_id,
                    'patientCode': patient_code,
                    'patientType': patient_type,
                    'doctorId': apt.doctor_id,
                    'doctorName': doctor_name,
                    'waiting': apt.waiting,
                    'checkedInTime': apt.checked_in_time.isoformat() + '-03:00' if apt.checked_in_time else None,
                    'phone': patient_phone,
                    'notes': apt.notes or ''
                }
            })
        except Exception as e:
            print(f"Erro ao processar agendamento {apt.id}: {e}")
            continue
    
    return jsonify(events)

@app.route('/api/patients/search_detailed')
@login_required
def search_detailed_patients():
    query_str = request.args.get('q', '').strip()
    if not query_str:
        return jsonify([])
    
    # Busca pacientes por nome ou CPF
    patients = Patient.query.filter(
        db.or_(
            Patient.name.ilike(f'%{query_str}%'),
            Patient.cpf.ilike(f'%{query_str}%')
        )
    ).all()
    
    results = []
    for p in patients:
        # Busca a última consulta (independente do médico para a secretária ver histórico geral)
        last_appointment = Appointment.query.filter_by(patient_id=p.id)\
            .order_by(Appointment.start_time.desc()).first()
        
        last_consult_date = last_appointment.start_time.strftime('%d/%m/%Y') if last_appointment else 'Nenhuma'
        
        # Prontuário/Código (para a secretária, podemos usar o ID ou um código global se existir)
        # O CRM usa PatientDoctor para códigos específicos por médico.
        # Vamos retornar o ID como número do prontuário geral.
        
        results.append({
            'id': p.id,
            'name': p.name,
            'cpf': p.cpf or '',
            'prontuario': p.id,
            'last_consult': last_consult_date
        })
    
    return jsonify(results)

@app.route('/api/patient/<int:id>/history')
@login_required
def get_patient_history(id):
    patient = Patient.query.get_or_404(id)
    notes = Note.query.filter_by(patient_id=id).order_by(Note.created_at.desc()).all()
    
    history = []
    for note in notes:
        history.append({
            'date': note.created_at.strftime('%d/%m/%Y %H:%M'),
            'category': note.category,
            'content': note.content,
            'doctor': note.doctor.name if note.doctor else 'Desconhecido'
        })
    
    return jsonify({
        'patient': {
            'id': patient.id,
            'name': patient.name,
            'phone': patient.phone,
            'cpf': patient.cpf,
            'birth_date': patient.birth_date,
            'address': patient.address,
            'city': patient.city,
            'patient_type': patient.patient_type
        },
        'history': history
    })

@app.route('/api/appointments/<int:appointment_id>', methods=['DELETE'])
@login_required
def delete_appointment_api(appointment_id):
    """Deleta um agendamento"""
    appointment = Appointment.query.get_or_404(appointment_id)
    
    # Se médico, só pode deletar seus próprios
    if current_user.is_doctor() and appointment.doctor_id != current_user.id:
        return jsonify({'success': False, 'error': 'Não autorizado'}), 403
    
    db.session.delete(appointment)
    db.session.commit()
    return jsonify({'success': True})

@app.route('/api/appointments', methods=['POST'])
@login_required
def create_appointment():
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({'success': False, 'error': 'Dados inválidos'}), 400
    
    # Se secretária, doctor_id vem do payload. Se médico, usa próprio ID
    if not current_user.is_doctor():
        doctor_id = data.get('doctor_id')
        if doctor_id:
            doctor_id = int(doctor_id)  # Converter string para int
    else:
        doctor_id = get_doctor_id()
    
    if not doctor_id:
        return jsonify({'success': False, 'error': 'Médico não especificado'}), 400
    
    # Buscar por nome normalizado (case-insensitive) para evitar duplicatas
    patient_name_input = data['patientName'].strip()
    patient = Patient.query.filter(db.func.lower(Patient.name) == db.func.lower(patient_name_input)).first()
    if not patient:
        # Converter strings vazias para None para campos opcionais
        birth_date_val = data.get('birth_date') or None
        phone_val = data.get('phone') or None
        cpf_val = data.get('cpf') or None
        address_val = data.get('address') or None
        city_val = data.get('city') or None
        mother_name_val = data.get('mother_name') or None
        indication_source_val = data.get('indication_source') or None
        occupation_val = data.get('occupation') or None
        
        patient = Patient(
            name=data['patientName'],
            phone=phone_val,
            email=data.get('email', ''),
            cpf=cpf_val,
            birth_date=birth_date_val,
            address=address_val,
            city=city_val,
            mother_name=mother_name_val,
            indication_source=indication_source_val,
            occupation=occupation_val,
            patient_type=data.get('patientType', 'particular')
        )
        db.session.add(patient)
        db.session.flush()
        
        # Handle photo for new patient
        if 'photo_data' in data and data['photo_data']:
            try:
                import base64
                import os
                from uuid import uuid4
                from PIL import Image
                from io import BytesIO
                
                photo_data = data['photo_data']
                if photo_data.startswith('data:image'):
                    header, encoded = photo_data.split(",", 1)
                    file_ext = header.split(";")[0].split("/")[1]
                    if file_ext == 'jpeg': file_ext = 'jpg'
                    
                    # Decodificar imagem
                    image_bytes = base64.b64decode(encoded)
                    img = Image.open(BytesIO(image_bytes))
                    
                    # Converter para RGB se necessário (remover transparência)
                    if img.mode in ("RGBA", "P"):
                        img = img.convert("RGB")
                    
                    # Redimensionar para tamanho 3x4 (proporcional)
                    # Exemplo: 300x400 pixels é suficiente para ficha
                    img.thumbnail((300, 400), Image.LANCZOS)
                    
                    filename = f"patient_{patient.id}_{uuid4().hex}.jpg"
                    filepath = os.path.join('static/uploads/photos', filename)
                    
                    os.makedirs(os.path.dirname(filepath), exist_ok=True)
                    
                    # Salvar com compressão máxima
                    img.save(filepath, "JPEG", quality=60, optimize=True)
                    
                    patient.photo_url = f"/{filepath}"
            except Exception as e:
                print(f"Erro ao processar foto: {e}")
    else:
        # Atualizar dados do paciente se fornecidos
        if 'patientType' in data:
            patient.patient_type = data['patientType']
        if 'phone' in data:
            patient.phone = data['phone']
        if 'cpf' in data:
            patient.cpf = data['cpf']
        if 'birth_date' in data and data['birth_date']:
            patient.birth_date = data['birth_date']
        if 'address' in data:
            patient.address = data['address']
        if 'city' in data:
            patient.city = data['city']
        if 'mother_name' in data:
            patient.mother_name = data['mother_name']
        if 'indication_source' in data:
            patient.indication_source = data['indication_source']
        if 'occupation' in data:
            patient.occupation = data['occupation']
    
    appointment = Appointment(
        patient_id=patient.id,
        doctor_id=doctor_id,
        start_time=parse_datetime_with_tz(data['start']),
        end_time=parse_datetime_with_tz(data['end']),
        status=data.get('status', 'agendado'),
        appointment_type=data.get('appointmentType', 'Particular'),
        notes=data.get('notes', '')
    )
    
    db.session.add(appointment)
    db.session.flush()
    
    # Criar ou obter registro PatientDoctor com código crescente
    pd = PatientDoctor.query.filter_by(patient_id=patient.id, doctor_id=doctor_id).first()
    if not pd:
        max_code = db.session.query(db.func.max(PatientDoctor.patient_code)).filter_by(doctor_id=doctor_id).scalar() or 0
        pd = PatientDoctor(patient_id=patient.id, doctor_id=doctor_id, patient_code=max_code + 1)
        db.session.add(pd)
    
    # Se for tipo de paciente Cirurgia, criar automaticamente no mapa cirúrgico
    surgery_created = False
    if data.get('patientType') == 'cirurgia' and data.get('surgery_name'):
        operating_room = OperatingRoom.query.first()
        if not operating_room:
            operating_room = OperatingRoom(name='Sala 1', capacity=1)
            db.session.add(operating_room)
            db.session.flush()
        
        start_dt = parse_datetime_with_tz(data['start'])
        end_dt = parse_datetime_with_tz(data['end'])
        
        surgery = Surgery(
            date=start_dt.date(),
            start_time=start_dt.time(),
            end_time=end_dt.time(),
            patient_id=patient.id,
            patient_name=patient.name,
            procedure_name=data['surgery_name'],
            doctor_id=doctor_id,
            operating_room_id=operating_room.id,
            status='agendada',
            notes=data.get('notes', ''),
            created_by=current_user.id
        )
        db.session.add(surgery)
        surgery_created = True
    
    db.session.commit()
    
    if surgery_created:
        try:
            from services.google_calendar import create_surgery_event
            create_surgery_event(
                patient_name=patient.name,
                procedure_name=data.get('surgery_name', 'Cirurgia'),
                surgery_date=surgery.date,
                start_time=surgery.start_time,
                end_time=surgery.end_time,
                notes=data.get('notes', '')
            )
        except Exception as cal_err:
            print(f"⚠ Google Calendar (não-crítico): {cal_err}")
    
    return jsonify({'success': True, 'id': appointment.id, 'surgery_created': surgery_created})

@app.route('/api/appointments/<int:id>', methods=['PUT'])
@login_required
def update_appointment(id):
    appointment = Appointment.query.get_or_404(id)
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({'success': False, 'error': 'Dados inválidos'}), 400
    
    if 'start' in data:
        appointment.start_time = parse_datetime_with_tz(data['start'])
    if 'end' in data:
        appointment.end_time = parse_datetime_with_tz(data['end'])
    if 'status' in data:
        appointment.status = data['status']
    if 'notes' in data:
        appointment.notes = data['notes']
    if 'appointment_type' in data:
        appointment.appointment_type = data['appointment_type']
    if 'appointmentType' in data:
        appointment.appointment_type = data['appointmentType']
    if 'patient_type' in data:
        appointment.patient.patient_type = data['patient_type']
    if 'patientType' in data:
        appointment.patient.patient_type = data['patientType']
    
    # Update patient phone if provided
    if 'phone' in data:
        appointment.patient.phone = data['phone']
    
    # Update patient photo if provided
    if 'photo_data' in data and data['photo_data']:
        try:
            import base64
            import os
            from uuid import uuid4
            from PIL import Image
            from io import BytesIO
            
            photo_data = data['photo_data']
            if photo_data.startswith('data:image'):
                header, encoded = photo_data.split(",", 1)
                image_bytes = base64.b64decode(encoded)
                img = Image.open(BytesIO(image_bytes))
                
                # Converter para RGB se necessário (remover transparência)
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                
                # Redimensionar para tamanho 3x4 (proporcional)
                img.thumbnail((300, 400), Image.LANCZOS)
                
                filename = f"patient_{appointment.patient.id}_{uuid4().hex}.jpg"
                filepath = os.path.join('static/uploads/photos', filename)
                
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                
                # Salvar com compressão máxima
                img.save(filepath, "JPEG", quality=60, optimize=True)
                
                appointment.patient.photo_url = f"/{filepath}"
        except Exception as e:
            print(f"Erro ao processar foto na edicao: {e}")

    # Update patient name if provided (find or update existing)
    if 'patientName' in data and data['patientName'] != appointment.patient.name:
        # Check if patient with new name already exists
        existing_patient = Patient.query.filter_by(name=data['patientName']).first()
        if existing_patient:
            # Link appointment to existing patient
            appointment.patient_id = existing_patient.id
        else:
            # Update patient name
            appointment.patient.name = data['patientName']
    
    db.session.commit()
    
    return jsonify({'success': True})

@app.route('/api/patient/<int:id>/photo', methods=['POST'])
@login_required
def update_patient_photo(id):
    patient = Patient.query.get_or_404(id)
    
    if 'photo' in request.files:
        # Upload via form-data
        file = request.files['photo']
        if file:
            try:
                from PIL import Image
                from uuid import uuid4
                import os
                
                img = Image.open(file.stream)
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                
                img.thumbnail((300, 400), Image.LANCZOS)
                
                filename = f"patient_{patient.id}_{uuid4().hex}.jpg"
                filepath = os.path.join('static/uploads/photos', filename)
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                
                img.save(filepath, "JPEG", quality=60, optimize=True)
                patient.photo_url = f"/{filepath}"
                db.session.commit()
                return jsonify({'success': True, 'photo_url': patient.photo_url})
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)}), 500
    
    data = request.get_json(silent=True)
    if data and 'photo_data' in data:
        # Upload via base64 (webcam)
        try:
            import base64
            from PIL import Image
            from io import BytesIO
            from uuid import uuid4
            import os
            
            photo_data = data['photo_data']
            if photo_data.startswith('data:image'):
                header, encoded = photo_data.split(",", 1)
                image_bytes = base64.b64decode(encoded)
                img = Image.open(BytesIO(image_bytes))
                
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                
                img.thumbnail((300, 400), Image.LANCZOS)
                
                filename = f"patient_{patient.id}_{uuid4().hex}.jpg"
                filepath = os.path.join('static/uploads/photos', filename)
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                
                img.save(filepath, "JPEG", quality=60, optimize=True)
                patient.photo_url = f"/{filepath}"
                db.session.commit()
                return jsonify({'success': True, 'photo_url': patient.photo_url})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
            
    return jsonify({'success': False, 'error': 'Nenhuma foto fornecida'}), 400

@app.route('/api/patients/search')
@login_required
def search_patients():
    query = request.args.get('q', '').strip()
    doctor_id = request.args.get('doctor_id', None)
    
    if not query or len(query) < 2:
        return jsonify([])
    
    # Convert doctor_id to int if provided and valid
    if doctor_id and doctor_id != 'null':
        try:
            doctor_id = int(doctor_id)
        except (ValueError, TypeError):
            doctor_id = None
    else:
        doctor_id = None
    
    # Buscar pacientes por nome (case-insensitive)
    patients = Patient.query.filter(Patient.name.ilike(f'%{query}%')).limit(10).all()
    
    result = []
    for patient in patients:
        patient_data = {
            'id': patient.id,
            'name': patient.name,
            'cpf': patient.cpf or '',
            'birth_date': patient.birth_date.isoformat() if patient.birth_date else '',
            'phone': patient.phone or '',
            'address': patient.address or '',
            'city': patient.city or '',
            'mother_name': patient.mother_name or '',
            'indication_source': patient.indication_source or '',
            'occupation': patient.occupation or '',
            'patient_type': patient.patient_type or 'particular'
        }
        
        # Se foi passado doctor_id válido, buscar código do paciente
        if doctor_id:
            pd = PatientDoctor.query.filter_by(patient_id=patient.id, doctor_id=doctor_id).first()
            patient_data['patient_code'] = pd.patient_code if pd else None
        
        result.append(patient_data)
    
    return jsonify(result)

@app.route('/api/patient/<int:patient_id>/today-appointment', methods=['GET'])
@login_required
def get_patient_today_appointment(patient_id):
    """Busca o agendamento de hoje para o paciente (para finalizar atendimento)"""
    today = get_brazil_time().date()
    
    # Buscar agendamento de hoje que ainda nao foi atendido
    appointment = Appointment.query.filter(
        Appointment.patient_id == patient_id,
        db.func.date(Appointment.start_time) == today,
        Appointment.status != 'atendido'
    ).order_by(Appointment.start_time.desc()).first()
    
    if appointment:
        print(f"DEBUG today-appointment: Encontrado appointment_id={appointment.id} para patient_id={patient_id}")
        return jsonify({'appointment_id': appointment.id})
    
    # Se nao encontrar pendente, buscar qualquer um de hoje
    appointment = Appointment.query.filter(
        Appointment.patient_id == patient_id,
        db.func.date(Appointment.start_time) == today
    ).order_by(Appointment.start_time.desc()).first()
    
    if appointment:
        print(f"DEBUG today-appointment: Encontrado (qualquer) appointment_id={appointment.id} para patient_id={patient_id}")
        return jsonify({'appointment_id': appointment.id})
    
    print(f"DEBUG today-appointment: Nenhum agendamento encontrado para patient_id={patient_id} em {today}")
    return jsonify({'appointment_id': None})

@app.route('/api/appointments/<int:id>/notes', methods=['GET'])
@login_required
def get_appointment_notes(id):
    appointment = Appointment.query.get_or_404(id)
    notes = Note.query.filter_by(appointment_id=id).all()
    
    result = {}
    for note in notes:
        result[note.note_type] = {
            'id': note.id,
            'content': note.content or ''
        }
    
    return jsonify(result)

@app.route('/api/notes/<int:note_id>', methods=['PUT'])
@login_required
def update_note(note_id):
    try:
        note = Note.query.get_or_404(note_id)
        data = request.get_json()
        
        if 'content' in data:
            note.content = data['content']
        
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao atualizar nota: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/appointments/<int:id>', methods=['DELETE'])
@login_required
def delete_appointment(id):
    appointment = Appointment.query.get_or_404(id)
    
    # Deletar todas as notas associadas
    Note.query.filter_by(appointment_id=id).delete()
    
    # Deletar o agendamento
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
    
    doctor = db.session.get(User, doctor_id)
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
    
    doctor = db.session.get(User, doctor_id)
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
    
    doctor = db.session.get(User, doctor_id)
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

@app.route('/api/patient/<int:patient_id>/update', methods=['POST'])
@login_required
def update_patient(patient_id):
    if not current_user.is_doctor() and not current_user.is_secretary():
        return jsonify({'success': False, 'error': 'Sem permissão'}), 403
    
    # Verificar acesso: Médicos só podem editar seus próprios pacientes
    if current_user.is_doctor():
        from models import PatientDoctor
        pd = PatientDoctor.query.filter_by(patient_id=patient_id, doctor_id=current_user.id).first()
        if not pd:
            return jsonify({'success': False, 'error': 'Sem acesso a este paciente'}), 403
    
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'success': False, 'error': 'Dados inválidos'}), 400
    
    patient = Patient.query.get_or_404(patient_id)
    
    if data.get('name'):
        patient.name = data['name']
    if 'email' in data:
        patient.email = data['email'] or None
    if 'phone' in data:
        patient.phone = data['phone'] or None
    if 'birth_date' in data:
        if data['birth_date']:
            from datetime import datetime
            patient.birth_date = datetime.strptime(data['birth_date'], '%Y-%m-%d').date()
        else:
            patient.birth_date = None
    if 'cpf' in data:
        patient.cpf = data['cpf'] or None
    if 'address' in data:
        patient.address = data['address'] or None
    if 'city' in data:
        patient.city = data['city'] or None
    if 'state' in data:
        patient.state = data['state'] or None
    if 'zip_code' in data:
        patient.zip_code = data['zip_code'] or None
    if 'mother_name' in data:
        patient.mother_name = data['mother_name'] or None
    if 'occupation' in data:
        patient.occupation = data['occupation'] or None
    if 'indication_source' in data:
        patient.indication_source = data['indication_source'] or None
    if 'patient_type' in data:
        patient.patient_type = data['patient_type'] or 'particular'
    
    db.session.commit()
    return jsonify({'success': True})

@app.route('/api/patient/<int:patient_id>/transplant-indication', methods=['POST'])
@login_required
def save_transplant_indication(patient_id):
    if not current_user.is_doctor():
        return jsonify({'success': False, 'error': 'Apenas médicos'}), 403
    
    # Verificar acesso: Médicos só podem editar seus próprios pacientes
    from models import PatientDoctor
    pd = PatientDoctor.query.filter_by(patient_id=patient_id, doctor_id=current_user.id).first()
    if not pd:
        return jsonify({'success': False, 'error': 'Sem acesso a este paciente'}), 403
    
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({'success': False, 'error': 'Dados inválidos'}), 400
    
    patient = Patient.query.get_or_404(patient_id)
    patient.has_transplant_indication = data.get('has_indication', False)
    db.session.commit()
    
    return jsonify({'success': True})

@app.route('/api/patient/<int:patient_id>/prescription', methods=['POST'])
@login_required
def save_prescription(patient_id):
    if not current_user.is_doctor():
        return jsonify({'success': False, 'error': 'Apenas médicos'}), 403
    
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({'success': False, 'error': 'Dados inválidos'}), 400
    
    prescription = Prescription(
        patient_id=patient_id,
        doctor_id=current_user.id,
        medications_oral=data.get('oral', []),
        medications_topical=data.get('topical', []),
        summary=data.get('summary', ''),
        prescription_type=data.get('type', 'standard')
    )
    db.session.add(prescription)
    db.session.commit()
    
    return jsonify({'success': True, 'id': prescription.id})

@app.route('/api/patient/<int:patient_id>/prescriptions', methods=['GET'])
@login_required
def get_prescriptions(patient_id):
    prescriptions = Prescription.query.filter_by(patient_id=patient_id)\
        .order_by(Prescription.created_at.desc()).limit(20).all()
    
    result = []
    for p in prescriptions:
        result.append({
            'id': p.id,
            'summary': p.summary or 'Receita sem resumo',
            'type': p.prescription_type,
            'created_at': p.created_at.strftime('%d/%m/%Y %H:%M') if p.created_at else '',
            'oral': p.medications_oral or [],
            'topical': p.medications_topical or []
        })
    
    return jsonify({'prescriptions': result})

@app.route('/prontuario/<int:patient_id>')
@login_required
def prontuario(patient_id):
    if not current_user.is_doctor() and not current_user.is_secretary():
        return redirect(url_for('agenda'))
    
    # Verificar acesso: Médicos veem apenas seus próprios pacientes, secretárias veem todos
    if current_user.is_doctor():
        from models import PatientDoctor
        pd = PatientDoctor.query.filter_by(patient_id=patient_id, doctor_id=current_user.id).first()
        if not pd:
            from flask import abort
            abort(403)
    
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
        
        # Obter appointment para pegar a data correta
        appointment = db.session.get(Appointment, appt_id)
        consultation_date = appointment.start_time if appointment else (finalized_note.created_at if finalized_note else first_note.created_at)
        
        consultations.append({
            'id': appt_id,  # Usar appointment_id como ID único
            'date': consultation_date,
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
    
    # Calcular idade do paciente
    age = None
    if patient.birth_date:
        from datetime import date
        today = date.today()
        age = today.year - patient.birth_date.year - ((today.month, today.day) < (patient.birth_date.month, patient.birth_date.day))
    
    return render_template('prontuario.html', 
                         patient=patient, 
                         procedures=procedures,
                         tags=tags,
                         patient_tags=patient_tags,
                         notes=notes,
                         consultations=consultations,
                         appointment_id=appointment_id,
                         age=age)

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

        # ATENÇÃO: Garantir status "atendido" e saída da sala de espera
        # Fazemos isso no início da transação para garantir que ocorra mesmo se houver erro posterior
        if appointment_id:
            try:
                # Buscar o agendamento sem restrição de médico para correção de bugs antigos
                appt = db.session.get(Appointment, int(appointment_id))
                if appt and appt.patient_id == patient_id:
                    appt.status = 'atendido'
                    appt.waiting = False
                    if not appt.checked_in_time:
                        appt.checked_in_time = get_brazil_time()
                    db.session.add(appt)
                    db.session.flush() # Força a ida para o DB dentro da transação
                    print(f"DEBUG CRÍTICO: Appointment {appointment_id} forçado para atendido")
            except Exception as appt_err:
                print(f"Erro ao atualizar status do agendamento: {appt_err}")

        
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
            # Capturar indicação de transplante
            transplant_indication = data.get('transplant_indication', 'nao')
            
            conduta_note = Note(
                patient_id=patient_id,
                doctor_id=current_user.id,
                appointment_id=appointment_id,  # Agrupa consultas
                note_type='conduta',
                category=category,  # Adicionar categoria
                content=conduta_content or '[Conduta registrada via procedimentos]',
                consultation_duration=duration,
                transplant_indication=transplant_indication
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
                # Batch update de lembretes ANTES do loop
                performed_proc_names = [p['name'] for p in procedures if p.get('performed', False)]
                non_performed_proc_names = [p['name'] for p in procedures if not p.get('performed', False)]
                
                # Cancelar lembretes para procedimentos realizados
                if performed_proc_names:
                    FollowUpReminder.query.filter(
                        FollowUpReminder.patient_id == patient_id,
                        FollowUpReminder.procedure_name.in_(performed_proc_names),
                        FollowUpReminder.reminder_type == 'cosmetic_follow_up',
                        FollowUpReminder.status == 'pending'
                    ).update({'status': 'completed'}, synchronize_session=False)
                
                # Marcar como superados os lembretes para procedimentos não realizados
                if non_performed_proc_names:
                    FollowUpReminder.query.filter(
                        FollowUpReminder.patient_id == patient_id,
                        FollowUpReminder.procedure_name.in_(non_performed_proc_names),
                        FollowUpReminder.reminder_type == 'cosmetic_follow_up',
                        FollowUpReminder.status == 'pending'
                    ).update({'status': 'superseded'}, synchronize_session=False)
                
                # Criar registros de plano e novos lembretes
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
                        follow_up_months=int(proc['months']),
                        observations=proc.get('observations', '')
                    )
                    db.session.add(plan)
                    
                    # Criar novo lembrete APENAS para não realizados
                    if not proc.get('performed', False):
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
                
                # Adicionar taxa de consulta conforme tipo de consulta (não baseado em tipo de paciente)
                # O tipo de consulta determina se cobra: Particular, Transplante Capilar = R$400
                # Retorno, UNIMED, Cortesia = sem cobrança
                total_amount = checkout_amount
                consultation_fee = CONSULTATION_PRICES.get(consultation_type, 0.0)
                if consultation_fee > 0:
                    procedures_list.insert(0, {
                        'name': f'Consulta {consultation_type}',
                        'value': consultation_fee
                    })
                    total_amount += consultation_fee
                
                payment = Payment(
                    appointment_id=appointment_id if appointment_id else None,
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
            import json
            
            surgical_planning = data.get('surgical_planning', {})
            conduta_note_id = note_ids.get('conduta')
            
            # Atualizar nota com planejamento cirúrgico
            if conduta_note_id:
                conduta_note = db.session.get(Note, conduta_note_id)
                if conduta_note:
                    conduta_note.surgical_planning = json.dumps(surgical_planning) if surgical_planning else None
            
            if conduta_note_id and surgical_planning:
                transplant = HairTransplant(
                    note_id=conduta_note_id,
                    norwood_classification=surgical_planning.get('norwood'),
                    previous_transplant=surgical_planning.get('previous_transplant', 'nao'),
                    transplant_location=surgical_planning.get('transplant_location'),
                    frontal_transplant=surgical_planning.get('frontal', False),
                    crown_transplant=surgical_planning.get('crown', False),
                    complete_transplant=surgical_planning.get('complete', False),
                    complete_with_body_hair=surgical_planning.get('complete_body_hair', False),
                    dense_packing=surgical_planning.get('dense_packing', False),
                    surgical_planning=surgical_planning.get('surgical_planning_text', ''),
                    clinical_conduct=data.get('conduta', '')
                )
                db.session.add(transplant)
        
        # Atualizar status do agendamento para "atendido"
        appointment_id = data.get('appointment_id')
        print(f"DEBUG finalizar: appointment_id={appointment_id}, patient_id={patient_id}, doctor_id={current_user.id}")
        
        if appointment_id:
            # Primeiro buscar sem filtro de doctor para debug
            appointment_check = Appointment.query.filter_by(id=appointment_id).first()
            if appointment_check:
                print(f"DEBUG: Appointment encontrado - doctor_id no DB: {appointment_check.doctor_id}, current_user.id: {current_user.id}")
            
            # Buscar o appointment (sem filtro de doctor_id para permitir atualizar)
            appointment = Appointment.query.filter_by(
                id=appointment_id,
                patient_id=patient_id
            ).first()
            
            if appointment:
                appointment.status = 'atendido'
                appointment.waiting = False
                if not appointment.checked_in_time:
                    appointment.checked_in_time = get_brazil_time()
                db.session.add(appointment)
                print(f"DEBUG: Appointment {appointment_id} updated to atendido, status={appointment.status}")
            else:
                print(f"Warning: Appointment {appointment_id} not found for patient {patient_id}")
        
        # Commit da transação
        db.session.commit()
        
        # === GOOGLE SHEETS: Registrar procedimentos realizados ===
        try:
            from services.google_sheets import append_procedures_batch
            from dateutil.relativedelta import relativedelta
            patient = Patient.query.get(patient_id)
            patient_name = patient.name if patient else f"Paciente #{patient_id}"
            patient_phone = patient.phone if patient else ''
            now = get_brazil_time()

            gs_rows = []
            if category == 'cosmiatria':
                for proc in data.get('cosmetic_procedures', []):
                    if proc.get('performed', False):
                        performed_date = now.date()
                        follow_up_months = proc.get('follow_up_months')
                        if follow_up_months and int(follow_up_months) > 0:
                            return_date = performed_date + relativedelta(months=int(follow_up_months))
                            return_date_str = return_date.strftime('%d/%m/%Y')
                        else:
                            return_date_str = ''
                        gs_rows.append({
                            'patient_name': patient_name,
                            'procedure_name': proc.get('name', 'Procedimento'),
                            'procedure_date': performed_date.strftime('%d/%m/%Y'),
                            'return_date': return_date_str,
                            'phone': patient_phone or '',
                        })

            if gs_rows:
                append_procedures_batch(gs_rows)
        except Exception as gs_error:
            print(f"⚠ Google Sheets (não-crítico): {gs_error}")
        
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
        feminine_hair_transplant=request.form.get('feminine_hair_transplant') == 'true',
        frontal_transplant=request.form.get('frontal') == 'true',
        crown_transplant=request.form.get('crown') == 'true',
        complete_transplant=request.form.get('complete') == 'true',
        complete_with_body_hair=request.form.get('complete_body_hair') == 'true',
        dense_packing=request.form.get('dense_packing') == 'true',
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
    
    recipient = db.session.get(User, int(recipient_id))
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
    
    plans = db.session.query(CosmeticProcedurePlan, Note).join(Note).filter(
        Note.patient_id == patient_id
    ).order_by(CosmeticProcedurePlan.id.desc()).all()
    
    plans_data = []
    for plan, note in plans:
        plans_data.append({
            'id': plan.id,
            'procedure_name': plan.procedure_name,
            'planned_value': plan.planned_value,
            'final_budget': plan.final_budget,
            'was_performed': plan.was_performed,
            'performed_date': plan.performed_date.isoformat() if plan.performed_date else None,
            'follow_up_months': plan.follow_up_months,
            'created_at': note.created_at.isoformat() if note else None
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
                appointment = db.session.get(Appointment, note.appointment_id)
            
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
# Tipos de consulta e seus valores - determina se cobra ou não
CONSULTATION_PRICES = {
    'Particular': 400.0,           # Cobra R$400
    'Transplante Capilar': 400.0,  # Cobra R$400
    'Retorno': 0.0,                # Não cobra
    'UNIMED': 0.0,                 # Não cobra
    'Cortesia': 0.0,               # Não cobra
    'Consulta Cortesia': 0.0       # Não cobra
}

@app.route('/api/checkout/pending', methods=['GET'])
@login_required
def get_pending_checkouts():
    if not current_user.is_secretary() and not current_user.is_doctor():
        return jsonify({'success': False, 'error': 'Não autorizado'}), 403
    
    today = get_brazil_time().date()
    
    payments = Payment.query.filter(
        db.func.date(Payment.created_at) == today
    ).all()
    
    print(f"DEBUG: Found {len(payments)} payments for today")
    
    data = []
    for payment in payments:
        patient = payment.patient
        apt_id = payment.appointment_id if payment.appointment_id else 'N/A'
        
        procedures = list(payment.procedures or [])
        consultation_type = payment.consultation_type or 'Particular'
        consultation_fee = CONSULTATION_PRICES.get(consultation_type, 0.0)
        
        has_consultation_item = any(p.get('name', '').startswith('Consulta') for p in procedures)
        
        # Apenas calcula o total sem reinserer automaticamente a consulta
        # A consulta é controlada manualmente pelo toggle do checkbox
        computed_total = sum(float(p.get('value', 0)) for p in procedures)
        
        # Atualiza total_amount se diferente do computado
        if payment.status == 'pendente' and abs(float(payment.total_amount) - computed_total) > 0.01:
            payment.total_amount = computed_total
            db.session.commit()
        
        data.append({
            'id': payment.id,
            'appointment_id': apt_id,
            'patient_name': patient.name if patient else 'Desconhecido',
            'consultation_type': consultation_type,
            'total_amount': computed_total,
            'procedures': procedures,
            'created_at': format_brazil_datetime(payment.created_at),
            'status': payment.status,
            'paid_at': format_brazil_datetime(payment.paid_at),
            'payment_method': payment.payment_method,
            'consultation_included': has_consultation_item
        })
        print(f"  - Payment {payment.id}: {patient.name if patient else '?'} R${computed_total} - {payment.status}")
    
    return jsonify({'success': True, 'checkouts': data})

@app.route('/api/checkout/create', methods=['POST'])
@login_required
def create_checkout():
    if not current_user.is_doctor() and not current_user.is_secretary():
        return jsonify({'success': False, 'error': 'Não autorizado'}), 403
    
    data = request.get_json(silent=True)
    if not data or 'appointment_id' not in data:
        return jsonify({'success': False, 'error': 'Dados inválidos'}), 400
    
    appointment = db.session.get(Appointment, data['appointment_id'])
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
    
    payment = db.session.get(Payment, payment_id)
    if not payment:
        return jsonify({'success': False, 'error': 'Pagamento não encontrado'}), 404
    
    payment.payment_method = data['payment_method']
    payment.installments = data.get('installments', 1)
    payment.status = 'pago'
    payment.paid_at = get_brazil_time()
    
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Pagamento registrado com sucesso'})

@app.route('/api/checkout/pending/count', methods=['GET'])
@login_required
def get_pending_checkout_count():
    """Retorna a contagem de checkouts pendentes do dia"""
    today = get_brazil_time().date()
    
    count = Payment.query.filter(
        db.func.date(Payment.created_at) == today,
        Payment.status == 'pendente'
    ).count()
    
    return jsonify({'success': True, 'count': count})

@app.route('/api/checkout/<int:payment_id>/toggle-consultation', methods=['POST'])
@login_required
def toggle_consultation_charge(payment_id):
    """Ativa ou desativa a cobrança da consulta no checkout"""
    from sqlalchemy.orm.attributes import flag_modified
    
    if not current_user.is_secretary():
        return jsonify({'success': False, 'error': 'Apenas secretárias'}), 403
    
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'success': False, 'error': 'Dados inválidos'}), 400
    
    payment = db.session.get(Payment, payment_id)
    if not payment:
        return jsonify({'success': False, 'error': 'Pagamento não encontrado'}), 404
    
    if payment.status != 'pendente':
        return jsonify({'success': False, 'error': 'Não é possível alterar pagamento já processado'}), 400
    
    charge_consultation = data.get('charge_consultation', True)
    consultation_type = payment.consultation_type or 'Particular'
    consultation_fee = CONSULTATION_PRICES.get(consultation_type, 400.0)
    
    # Validar: não permitir marcar como cobrada se a consulta é gratuita
    if charge_consultation and consultation_fee == 0:
        return jsonify({'success': False, 'error': 'Consulta gratuita não pode ser cobrada'}), 400
    
    # Criar CÓPIA da lista para forçar detecção de mudança pelo SQLAlchemy
    procedures = list(payment.procedures or [])
    
    if charge_consultation:
        # Adicionar consulta se não existe
        has_consultation = any(p.get('name', '').startswith('Consulta') for p in procedures)
        if not has_consultation:
            consultation_item = {
                'name': f'Consulta {consultation_type}',
                'value': consultation_fee
            }
            procedures.insert(0, consultation_item)
    else:
        # Remover consulta - criar nova lista sem itens de consulta
        procedures = [p for p in procedures if not p.get('name', '').startswith('Consulta')]
    
    # Recalcular total
    new_total = sum(float(p.get('value', 0)) for p in procedures)
    
    # Atribuir nova lista e marcar como modificado
    payment.procedures = procedures
    payment.total_amount = new_total
    flag_modified(payment, 'procedures')
    
    db.session.commit()
    
    print(f"DEBUG toggle: Payment {payment_id} - new_total={new_total}, procedures={procedures}")
    
    return jsonify({
        'success': True, 
        'new_total': new_total,
        'procedures': procedures,
        'message': 'Consulta ' + ('incluída' if charge_consultation else 'removida') + ' com sucesso'
    })

# ============ EVOLUTION ENDPOINTS ============
@app.route('/api/patient/<int:patient_id>/evolutions', methods=['GET'])
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
        
        consultation_data = {
            'id': consultation.id,
            'date': consultation.start_time.strftime('%d/%m/%Y %H:%M'),
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

@app.route('/api/patient/<int:patient_id>/evolution', methods=['POST'])
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

@app.route('/api/evolution/<int:evo_id>', methods=['PUT'])
@login_required
def update_evolution(evo_id):
    """Editar evolução"""
    evo = Evolution.query.get_or_404(evo_id)
    if evo.doctor_id != current_user.id and not current_user.is_admin():
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

@app.route('/api/evolution/<int:evo_id>', methods=['DELETE'])
@login_required
def delete_evolution(evo_id):
    """Deletar evolução"""
    evo = Evolution.query.get_or_404(evo_id)
    if evo.doctor_id != current_user.id and not current_user.is_admin():
        return jsonify({'success': False, 'error': 'Não autorizado'}), 403
    
    db.session.delete(evo)
    db.session.commit()
    return jsonify({'success': True})

# Upload de foto do paciente
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads', 'photos')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/patient/<int:patient_id>/photo', methods=['POST'])
@login_required
def upload_patient_photo(patient_id):
    """Upload de foto 3x4 do paciente"""
    patient = Patient.query.get_or_404(patient_id)
    
    if 'photo' not in request.files:
        return jsonify({'success': False, 'error': 'Nenhuma foto enviada'}), 400
    
    file = request.files['photo']
    if not file.filename:
        return jsonify({'success': False, 'error': 'Nenhum arquivo selecionado'}), 400
    
    if file and allowed_file(file.filename):
        import uuid
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"patient_{patient_id}_{uuid.uuid4().hex[:8]}.{ext}"
        
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        photo_url = f"/static/uploads/photos/{filename}"
        patient.photo_url = photo_url
        db.session.commit()
        
        return jsonify({'success': True, 'photo_url': photo_url})
    
    return jsonify({'success': False, 'error': 'Tipo de arquivo não permitido'}), 400

@app.route('/api/patient/<int:patient_id>/photo', methods=['DELETE'])
@login_required
def delete_patient_photo(patient_id):
    """Remover foto do paciente"""
    patient = Patient.query.get_or_404(patient_id)
    
    if patient.photo_url:
        try:
            filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), patient.photo_url.lstrip('/'))
            if os.path.exists(filepath):
                os.remove(filepath)
        except:
            pass
        
        patient.photo_url = None
        db.session.commit()
    
    return jsonify({'success': True})

# ========== AUTO-FALTOU SCHEDULER ==========
from apscheduler.schedulers.background import BackgroundScheduler

def _run_in_app_context(app_instance, fn):
    with app_instance.app_context():
        changed = fn()
        if changed > 0:
            print(f"[AUTO-FALTOU] {changed} agendamentos marcados como faltou")

def start_smart_no_show_scheduler(app_instance):
    tz = pytz.timezone("America/Sao_Paulo")
    scheduler = BackgroundScheduler(timezone=tz)

    from services.auto_no_show_service import mark_no_shows_grace_minutes

    scheduler.add_job(
        func=lambda: _run_in_app_context(app_instance, lambda: mark_no_shows_grace_minutes(30)),
        trigger="interval",
        minutes=5,
        id="smart_no_show_30min",
        replace_existing=True
    )

    scheduler.start()
    print("[AUTO-FALTOU] Scheduler iniciado - verificando a cada 5 minutos")

start_smart_no_show_scheduler(app)

# Note: When using Gunicorn for production, app.run() is not needed
# Gunicorn handles the server execution
if __name__ == '__main__':
    import os
    # Development server - runs when executed as script
    # Production uses Gunicorn (see deploy_config_tool settings)
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=5000, debug=debug_mode)

# APIs de Cirurgias de Transplante Capilar
@login_required
def get_surgeries(ht_id):
    from models import TransplantSurgery
    surgeries = TransplantSurgery.query.filter_by(hair_transplant_id=ht_id).order_by(TransplantSurgery.surgery_date.desc()).all()
    return jsonify([{
        'id': s.id,
        'surgery_date': s.surgery_date.isoformat(),
        'surgical_planning': s.surgical_planning,
        'complications': s.complications,
    } for s in surgeries])

@login_required
def create_surgery(ht_id):
    if not current_user.is_doctor():
        return jsonify({'success': False, 'error': 'Apenas médicos'}), 403
    
    from models import TransplantSurgery, HairTransplant
    from datetime import datetime
    
    ht = HairTransplant.query.get_or_404(ht_id)
    data = request.get_json()
    
    surgery = TransplantSurgery(
        hair_transplant_id=ht_id,
        surgery_date=datetime.fromisoformat(data.get('surgery_date')),
        surgical_planning=data.get('surgical_planning', ''),
        complications=data.get('complications', '')
    )
    db.session.add(surgery)
    db.session.commit()
    
    return jsonify({'success': True, 'id': surgery.id})

# API para gerenciar cirurgias por paciente
@login_required
def get_patient_surgeries(patient_id):
    """Listar todas as cirurgias de um paciente"""
    from models import TransplantSurgeryRecord
    surgeries = TransplantSurgeryRecord.query.filter_by(patient_id=patient_id).order_by(TransplantSurgeryRecord.surgery_date.desc()).all()
    return jsonify([{
        'id': s.id,
        'surgery_date': s.surgery_date.strftime('%d/%m/%Y'),
        'surgery_date_iso': s.surgery_date.isoformat(),
        'surgical_data': s.surgical_data,
        'observations': s.observations,
        'doctor_name': s.doctor.name
    } for s in surgeries])

@login_required
def create_patient_surgery(patient_id):
    """Criar nova cirurgia para um paciente"""
    if not current_user.is_doctor():
        return jsonify({'success': False, 'error': 'Apenas médicos'}), 403
    
    from models import TransplantSurgeryRecord
    from datetime import datetime
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

@app.route('/api/surgery/<int:surgery_id>', methods=['DELETE'])
@login_required
def delete_patient_surgery(surgery_id):
    """Deletar uma cirurgia"""
    from models import TransplantSurgeryRecord
    if not current_user.is_doctor():
        return jsonify({'success': False, 'error': 'Apenas médicos'}), 403
    
    surgery = TransplantSurgeryRecord.query.get_or_404(surgery_id)
    if surgery.doctor_id != current_user.id and not current_user.is_admin():
        return jsonify({'success': False, 'error': 'Não autorizado'}), 403
    
    db.session.delete(surgery)
    db.session.commit()
    
    return jsonify({'success': True})

@app.route('/api/surgery/<int:surgery_id>/evolutions', methods=['GET'])
@login_required
def get_surgery_evolutions(surgery_id):
    """Listar evoluções de uma cirurgia"""
    from models import TransplantSurgeryRecord, SurgeryEvolution
    surgery = TransplantSurgeryRecord.query.get_or_404(surgery_id)
    
    evolutions = SurgeryEvolution.query.filter_by(surgery_id=surgery_id).order_by(SurgeryEvolution.evolution_date.desc()).all()
    
    days_since = (get_brazil_time().date() - surgery.surgery_date).days
    
    return jsonify({
        'surgery_id': surgery_id,
        'surgery_date': surgery.surgery_date.isoformat(),
        'days_since_surgery': days_since,
        'evolutions': [{
            'id': e.id,
            'evolution_type': e.evolution_type,
            'evolution_date': e.evolution_date.isoformat(),
            'content': e.content,
            'has_necrosis': e.has_necrosis,
            'has_scabs': e.has_scabs,
            'has_infection': e.has_infection,
            'has_follicle_loss': e.has_follicle_loss,
            'result_rating': e.result_rating,
            'needs_another_surgery': e.needs_another_surgery,
            'doctor_name': e.doctor.name if e.doctor else 'Desconhecido'
        } for e in evolutions]
    })

@app.route('/api/surgery/<int:surgery_id>/evolution', methods=['POST'])
@login_required
def create_surgery_evolution(surgery_id):
    """Criar evolução pós-cirúrgica"""
    if not current_user.is_doctor():
        return jsonify({'success': False, 'error': 'Apenas médicos'}), 403
    
    from models import TransplantSurgeryRecord, SurgeryEvolution, FollowUpReminder
    surgery = TransplantSurgeryRecord.query.get_or_404(surgery_id)
    data = request.get_json()
    
    evolution_type = data.get('evolution_type', 'general')
    if evolution_type == 'rotina':
        evolution_type = 'general'
    if evolution_type not in ['general', '7_days', '1_year']:
        evolution_type = 'general'
    
    evolution = SurgeryEvolution(
        surgery_id=surgery_id,
        doctor_id=current_user.id,
        content=data.get('content', ''),
        evolution_type=evolution_type,
        has_necrosis=data.get('has_necrosis', False),
        has_scabs=data.get('has_scabs', False),
        has_infection=data.get('has_infection', False),
        has_follicle_loss=data.get('has_follicle_loss', False),
        result_rating=data.get('result_rating'),
        needs_another_surgery=data.get('needs_another_surgery', False)
    )
    
    db.session.add(evolution)
    
    if data.get('needs_another_surgery'):
        reminder = FollowUpReminder(
            patient_id=surgery.patient_id,
            procedure_name='Nova Cirurgia de Transplante Capilar',
            scheduled_date=get_brazil_time().date(),
            reminder_type='transplant_revision',
            status='pending',
            notes=f'Paciente indicado para nova cirurgia na evolução de 1 ano. Observações: {data.get("content", "")}'
        )
        db.session.add(reminder)
    
    db.session.commit()
    
    return jsonify({'success': True, 'id': evolution.id, 'evolution_type': evolution_type})

@app.route('/api/surgery/evolution/<int:evolution_id>', methods=['DELETE'])
@login_required
def delete_surgery_evolution(evolution_id):
    """Deletar uma evolução"""
    from models import SurgeryEvolution
    if not current_user.is_doctor():
        return jsonify({'success': False, 'error': 'Apenas médicos'}), 403
    
    evolution = SurgeryEvolution.query.get_or_404(evolution_id)
    db.session.delete(evolution)
    db.session.commit()
    
    return jsonify({'success': True})

# API para listar consultas (para dropdown de evolução)
@app.route('/api/patient/<int:patient_id>/consultations', methods=['GET'])
@login_required
def get_patient_consultations(patient_id):
    from models import Appointment, User
    appointments = Appointment.query.filter_by(patient_id=patient_id).order_by(Appointment.start_time.desc()).all()
    consultations = [{
        'id': apt.id,
        'date': apt.start_time.strftime('%d/%m/%Y %H:%M'),
        'category': apt.notes or 'Consulta'
    } for apt in appointments]
    return jsonify({'consultations': consultations})

# ==================== SALA DE ESPERA / CHECK-IN ====================
# Rotas movidas para routes/waiting_room.py (blueprint)

