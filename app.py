from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, send_file, make_response, abort
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
from models import db, User, Patient, PatientPhoto, Appointment, Note, Procedure, Indication, Tag, PatientTag, ChatMessage, MessageRead, CosmeticProcedurePlan, ProcedureExecution, HairTransplant, TransplantImage, FollowUpReminder, Payment, PatientDoctor, Evolution, Surgery, OperatingRoom, Prescription, CommercialTask, PushSubscription, PatientActivationLog
from services.patient_photo_service import delete_patient_photo as delete_stored_patient_photo
from services.patient_photo_service import save_patient_photo, save_patient_photo_data_url
from utils.database_backup import backup_manager
from services.access_control import can_manage_owned_record
from services.clinic_time import clinic_now, clinic_today, clinic_wall_time_iso, utc_instant_to_clinic_iso, get_brazil_time, parse_datetime_with_tz, format_brazil_datetime
from services.patient_identity import NEW_PATIENT_CODE_START, generate_next_patient_code, normalize_patient_name, find_possible_duplicate_patients
from services.execution_service import _parse_date_or_datetime, _serialize_execution, _build_execution_from_payload
from services.finalization_service import _note_counts_as_finalized, _find_finalized_note, _resolve_consultation_finalization
from services.timeline_service import build_patient_timeline
from services.doctor_service import get_doctor_id, get_all_doctors
from services.statuses import normalize_appointment_status

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


def _ensure_patient_doctor_partial_index():
    """Garante que o índice único parcial exista no banco de dados (PostgreSQL).

    É idempotente (IF NOT EXISTS) e roda uma vez no startup do app, garantindo
    que o banco de produção também possua a proteção de unicidade para códigos
    na faixa nova (>= 1001). Não afeta tabelas/códigos históricos.
    """
    try:
        if db.engine.dialect.name == 'postgresql':
            with db.engine.begin() as conn:
                conn.execute(db.text("""
                    CREATE UNIQUE INDEX IF NOT EXISTS idx_unique_new_code
                    ON patient_doctor (doctor_id, patient_code)
                    WHERE patient_code >= 1001;
                """))
    except Exception as e:
        app.logger.warning(f"Não foi possível garantir idx_unique_new_code: {e}")


def _ensure_physical_agenda_import_log_schema():
    try:
        from services.physical_agenda_schema_service import ensure_physical_agenda_import_schema
        ensure_physical_agenda_import_schema()
    except Exception as e:
        app.logger.warning(f"Não foi possível garantir physical_agenda_import_log: {e}")


# Executar a verificação do índice uma vez no startup (idempotente)
# Adiado para evitar que falhas de conexão no import do módulo
# quebrem o startup em produção. Rodará no primeiro request.
@app.before_request
def _ensure_index_on_startup():
    _ensure_patient_doctor_partial_index()
    _ensure_physical_agenda_import_log_schema()
    # Remove o handler após a primeira execução (safe para workers concorrentes)
    try:
        app.before_request_funcs[None].remove(_ensure_index_on_startup)
    except ValueError:
        pass


# Faixa inicial da nova política de códigos de paciente (FASE 1).
# Novos pacientes recebem códigos a partir de 1001. Códigos históricos
# (< 1001) são preservados integralmente e nunca alterados aqui.


from flask_wtf.csrf import CSRFError

@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    """Quando o token CSRF expira, voltar para o login com mensagem amigável em vez de erro 400."""
    flash('Sua sessão expirou. Por favor, faça login novamente.', 'warning')
    return redirect(url_for('login'))

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
from routes.cp import cp_bp
from routes.push import push_bp
from routes.physical_agenda import physical_agenda_bp

app.register_blueprint(surgical_map_bp)
app.register_blueprint(waiting_room_bp)
app.register_blueprint(settings_bp)
app.register_blueprint(crm_bp)
app.register_blueprint(dermascribe_bp)
app.register_blueprint(cp_bp)
app.register_blueprint(push_bp)
app.register_blueprint(physical_agenda_bp)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))
app.register_blueprint(patient_bp)

@app.route('/apple-touch-icon.png')
@app.route('/apple-touch-icon-precomposed.png')
def apple_touch_icon():
    return send_file('static/img/icons/apple-touch-icon.png', mimetype='image/png')

@app.route('/icon-192.png')
def icon_192():
    return send_file('static/img/icons/icon-192.png', mimetype='image/png')

@app.route('/icon-512.png')
def icon_512():
    return send_file('static/img/icons/icon-512.png', mimetype='image/png')

@app.route('/icon-1024.png')
def icon_1024():
    return send_file('static/img/icons/icon-1024.png', mimetype='image/png')

@app.route('/manifest.json')
def manifest():
    return send_file('static/manifest.json', mimetype='application/manifest+json')

@app.route('/service-worker.js')
def service_worker():
    response = send_file('static/service-worker.js', mimetype='application/javascript')
    response.headers['Service-Worker-Allowed'] = '/'
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response


@app.route('/api/cosmetic-plans/<int:plan_id>/perform', methods=['POST'])
@login_required
def perform_cosmetic_plan(plan_id):
    if not current_user.is_doctor() and not current_user.is_secretary():
        return jsonify({'success': False, 'error': 'Não autorizado'}), 403

    plan = CosmeticProcedurePlan.query.get_or_404(plan_id)
    data = request.get_json(silent=True) or {}
    performed_date = _parse_date_or_datetime(data.get('performed_date')) or get_brazil_time()

    try:
        execution = _build_execution_from_payload(plan, {
            'execution_status': 'realizada',
            'performed_date': performed_date.isoformat(),
            'charged_value': data.get('charged_value', plan.final_budget or plan.planned_value),
            'notes': data.get('notes') or data.get('observations'),
            'followup_date': data.get('followup_date'),
            'followup_status': data.get('followup_status', 'pendente')
        }, force_performed=True)
    except ValueError as exc:
        return jsonify({'success': False, 'error': str(exc)}), 400

    db.session.add(execution)
    db.session.commit()
    return jsonify({'success': True, 'execution': _serialize_execution(execution)})


@app.route('/api/cosmetic-plans/<int:plan_id>/executions', methods=['POST'])
@login_required
def create_plan_execution(plan_id):
    if not current_user.is_doctor() and not current_user.is_secretary():
        return jsonify({'success': False, 'error': 'Não autorizado'}), 403

    plan = CosmeticProcedurePlan.query.get_or_404(plan_id)
    data = request.get_json(silent=True) or {}

    idempotency_key = (data.get('idempotency_key') or request.headers.get('X-Idempotency-Key') or '').strip()
    if idempotency_key:
        existing = ProcedureExecution.query.filter_by(idempotency_key=idempotency_key, plan_id=plan.id).first()
        if existing:
            return jsonify({'success': True, 'execution': _serialize_execution(existing), 'idempotent_replay': True}), 200

    try:
        execution = _build_execution_from_payload(plan, data)
    except ValueError as exc:
        return jsonify({'success': False, 'error': str(exc)}), 400

    db.session.add(execution)
    db.session.commit()
    app.logger.info('execution_created id=%s plan_id=%s user_id=%s', execution.id, plan.id, current_user.id)
    
    # Sincronizar com Google Sheets se foi marcado como realizado
    if execution.execution_status == 'realizada':
        try:
            from threading import Thread
            def sync_sheets():
                from routes.crm import _get_performed_procedures_historical
                from services.google_sheets import _get_access_token, format_phone_for_sheets
                import requests as req
                
                patients_dict = {}
                try:
                    with app.app_context():
                        patients_dict = _get_performed_procedures_historical()
                except Exception as ctx_err:
                    app.logger.error(f'Erro no app context sync_sheets: {ctx_err}')
                    return
                
                if patients_dict:
                    SPREADSHEET_ID = '1IUNWhBRzt5u6_ttfzjfTKckhSMOMx1l_s7uGnIom66o'
                    SHEET_NAME = 'Procedimentos Realizados'
                    
                    rows = [['Paciente', 'Telefone', 'Status', 'Temperatura', 'Procedimentos Realizados', 'Total Realizado (R$)', 'Última Realização']]
                    for pd in patients_dict.values():
                        procs_str = '; '.join([
                            f"{p['procedure_name']} ({p['performed_date'][:10] if p['performed_date'] else 'N/A'}) - R$ {float(p['charged_value']):.2f}"
                            for p in pd['procedures']
                        ])
                        last_date = pd.get('last_performed_date', '')[:10] if pd.get('last_performed_date') else ''
                        rows.append([
                            pd['patient_name'],
                            format_phone_for_sheets(pd.get('patient_phone', '')),
                            pd.get('funnel_status', 'Realizado'),
                            pd.get('funnel_temperature', ''),
                            procs_str,
                            f"{float(pd['total_value']):.2f}",
                            str(last_date),
                        ])
                    
                    try:
                        access_token = _get_access_token()
                        headers = {
                            'Authorization': f'Bearer {access_token}',
                            'Content-Type': 'application/json'
                        }
                        base = f'https://sheets.googleapis.com/v4/spreadsheets/{SPREADSHEET_ID}'
                        
                        meta = req.get(f'{base}?fields=sheets.properties.title', headers=headers, timeout=10)
                        sheet_titles = [s['properties']['title'] for s in meta.json().get('sheets', [])] if meta.status_code == 200 else []
                        
                        if SHEET_NAME not in sheet_titles:
                            req.post(f'{base}:batchUpdate', headers=headers, timeout=10, json={
                                'requests': [{'addSheet': {'properties': {'title': SHEET_NAME}}}]
                            })
                        
                        req.post(f'{base}/values/{SHEET_NAME}!A1:Z2000:clear', headers=headers, timeout=10)
                        req.put(
                            f'{base}/values/{SHEET_NAME}!A1',
                            headers=headers,
                            timeout=15,
                            params={'valueInputOption': 'USER_ENTERED'},
                            json={'values': rows}
                        )
                        app.logger.info('Google Sheets sincronizado automaticamente - procedimento realizado')
                    except Exception as e:
                        app.logger.error(f'Erro ao sincronizar Google Sheets: {e}')
            
            thread = Thread(target=sync_sheets, daemon=True)
            thread.start()
        except Exception as e:
            app.logger.error(f'Erro ao iniciar sincronização Google Sheets: {e}')
    
    return jsonify({'success': True, 'execution': _serialize_execution(execution)}), 201


@app.route('/api/cosmetic-plans/<int:plan_id>/executions', methods=['GET'])
@login_required
def list_plan_executions(plan_id):
    if not current_user.is_doctor() and not current_user.is_secretary():
        return jsonify({'success': False, 'error': 'Não autorizado'}), 403

    CosmeticProcedurePlan.query.get_or_404(plan_id)
    executions = ProcedureExecution.query.filter_by(plan_id=plan_id).order_by(
        ProcedureExecution.performed_date.desc().nullslast(),
        ProcedureExecution.created_at.desc()
    ).all()
    return jsonify({'success': True, 'executions': [_serialize_execution(e) for e in executions]})


@app.route('/api/executions', methods=['GET'])
@login_required
def list_executions():
    if not current_user.is_doctor() and not current_user.is_secretary():
        return jsonify({'success': False, 'error': 'Não autorizado'}), 403

    query = db.session.query(ProcedureExecution).join(CosmeticProcedurePlan, ProcedureExecution.plan_id == CosmeticProcedurePlan.id).join(Note, CosmeticProcedurePlan.note_id == Note.id)
    if current_user.is_doctor():
        query = query.filter(Note.doctor_id == current_user.id)

    if request.args.get('doctor_id', type=int):
        query = query.filter(Note.doctor_id == request.args.get('doctor_id', type=int))
    if request.args.get('procedure_name'):
        query = query.filter(CosmeticProcedurePlan.procedure_name == request.args.get('procedure_name'))
    if request.args.get('execution_status'):
        query = query.filter(ProcedureExecution.execution_status == request.args.get('execution_status'))
    if request.args.get('date_from'):
        date_from = _parse_date_or_datetime(request.args.get('date_from'))
        query = query.filter(db.or_(ProcedureExecution.scheduled_date >= date_from, ProcedureExecution.performed_date >= date_from))
    if request.args.get('date_to'):
        date_to = _parse_date_or_datetime(request.args.get('date_to'))
        query = query.filter(db.or_(ProcedureExecution.scheduled_date <= date_to, ProcedureExecution.performed_date <= date_to))

    page = max(request.args.get('page', 1, type=int), 1)
    per_page = min(max(request.args.get('per_page', 20, type=int), 1), 100)
    total = query.count()
    rows = query.order_by(ProcedureExecution.created_at.desc()).offset((page - 1) * per_page).limit(per_page).all()
    return jsonify({'success': True, 'total': total, 'page': page, 'per_page': per_page, 'executions': [_serialize_execution(e) for e in rows]})


@app.route('/api/executions/<int:execution_id>', methods=['PUT'])
@login_required
def update_execution(execution_id):
    if not current_user.is_doctor() and not current_user.is_secretary():
        return jsonify({'success': False, 'error': 'Não autorizado'}), 403

    execution = ProcedureExecution.query.get_or_404(execution_id)
    data = request.get_json(silent=True) or {}

    if 'scheduled_date' in data:
        execution.scheduled_date = _parse_date_or_datetime(data.get('scheduled_date'))
    if 'performed_date' in data:
        execution.performed_date = _parse_date_or_datetime(data.get('performed_date'))
    if 'execution_status' in data:
        execution.execution_status = (data.get('execution_status') or '').strip().lower()
    elif 'was_performed' in data:
        execution.execution_status = 'realizada' if bool(data.get('was_performed')) else 'agendada'

    if execution.execution_status == 'realizada' and not execution.performed_date:
        return jsonify({'success': False, 'error': 'performed_date é obrigatório quando execution_status=realizada'}), 400
    if execution.execution_status == 'agendada' and not execution.scheduled_date:
        return jsonify({'success': False, 'error': 'scheduled_date é obrigatório quando execution_status=agendada'}), 400

    execution.was_performed = execution.execution_status == 'realizada'

    if 'charged_value' in data:
        raw = data.get('charged_value')
        if raw in (None, ''):
            execution.charged_value = None
        else:
            value = float(raw)
            if value < 0:
                return jsonify({'success': False, 'error': 'charged_value não pode ser negativo'}), 400
            execution.charged_value = value
    if 'notes' in data:
        execution.notes = data.get('notes')
    if 'followup_date' in data:
        execution.followup_date = _parse_date_or_datetime(data.get('followup_date'))
    if 'followup_status' in data:
        status = (data.get('followup_status') or '').strip().lower()
        if status not in {'pendente', 'contatado', 'agendado', 'sem_resposta'}:
            return jsonify({'success': False, 'error': 'followup_status inválido'}), 400
        execution.followup_status = status

    execution.updated_by = current_user.id
    execution.updated_at = get_brazil_time()
    
    was_realizado = execution.execution_status == 'realizada'

    db.session.commit()
    app.logger.info('execution_updated id=%s plan_id=%s user_id=%s', execution.id, execution.plan_id, current_user.id)
    
    # Sincronizar com Google Sheets se foi marcado como realizado
    if was_realizado:
        try:
            from threading import Thread
            def sync_sheets():
                from routes.crm import _get_performed_procedures_historical
                from services.google_sheets import _get_access_token, format_phone_for_sheets
                import requests as req
                
                patients_dict = _get_performed_procedures_historical()
                if patients_dict:
                    SPREADSHEET_ID = '1IUNWhBRzt5u6_ttfzjfTKckhSMOMx1l_s7uGnIom66o'
                    SHEET_NAME = 'Procedimentos Realizados'
                    
                    rows = [['Paciente', 'Telefone', 'Status', 'Temperatura', 'Procedimentos Realizados', 'Total Realizado (R$)', 'Última Realização']]
                    for pd in patients_dict.values():
                        procs_str = '; '.join([
                            f"{p['procedure_name']} ({p['performed_date'][:10] if p['performed_date'] else 'N/A'}) - R$ {float(p['charged_value']):.2f}"
                            for p in pd['procedures']
                        ])
                        last_date = pd.get('last_performed_date', '')[:10] if pd.get('last_performed_date') else ''
                        rows.append([
                            pd['patient_name'],
                            format_phone_for_sheets(pd.get('patient_phone', '')),
                            pd.get('funnel_status', 'Realizado'),
                            pd.get('funnel_temperature', ''),
                            procs_str,
                            f"{float(pd['total_value']):.2f}",
                            str(last_date),
                        ])
                    
                    try:
                        access_token = _get_access_token()
                        headers = {
                            'Authorization': f'Bearer {access_token}',
                            'Content-Type': 'application/json'
                        }
                        base = f'https://sheets.googleapis.com/v4/spreadsheets/{SPREADSHEET_ID}'
                        
                        meta = req.get(f'{base}?fields=sheets.properties.title', headers=headers, timeout=10)
                        sheet_titles = [s['properties']['title'] for s in meta.json().get('sheets', [])] if meta.status_code == 200 else []
                        
                        if SHEET_NAME not in sheet_titles:
                            req.post(f'{base}:batchUpdate', headers=headers, timeout=10, json={
                                'requests': [{'addSheet': {'properties': {'title': SHEET_NAME}}}]
                            })
                        
                        req.post(f'{base}/values/{SHEET_NAME}!A1:Z2000:clear', headers=headers, timeout=10)
                        req.put(
                            f'{base}/values/{SHEET_NAME}!A1',
                            headers=headers,
                            timeout=15,
                            params={'valueInputOption': 'USER_ENTERED'},
                            json={'values': rows}
                        )
                        app.logger.info('Google Sheets sincronizado automaticamente - procedimento atualizado')
                    except Exception as e:
                        app.logger.error(f'Erro ao sincronizar Google Sheets: {e}')
            
            thread = Thread(target=sync_sheets, daemon=True)
            thread.start()
        except Exception as e:
            app.logger.error(f'Erro ao iniciar sincronização Google Sheets: {e}')
    
    return jsonify({'success': True, 'execution': _serialize_execution(execution)})


@app.route('/api/executions/<int:execution_id>', methods=['DELETE'])
@login_required
def delete_execution(execution_id):
    if not current_user.is_doctor() and not current_user.is_secretary():
        return jsonify({'success': False, 'error': 'Não autorizado'}), 403

    execution = ProcedureExecution.query.get_or_404(execution_id)
    plan = db.session.query(CosmeticProcedurePlan).join(Note, CosmeticProcedurePlan.note_id == Note.id).filter(
        CosmeticProcedurePlan.id == execution.plan_id
    ).first()
    if not plan:
        return jsonify({'success': False, 'error': 'Planejamento não encontrado'}), 404
    if current_user.is_doctor() and plan.note.doctor_id != current_user.id:
        return jsonify({'success': False, 'error': 'Não autorizado'}), 403

    db.session.delete(execution)
    db.session.commit()
    app.logger.info('execution_deleted id=%s plan_id=%s user_id=%s', execution.id, execution.plan_id, current_user.id)
    return jsonify({'success': True})

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
    
    surgery_ids_subq = db.session.query(TransplantSurgeryRecord.id).filter(
        TransplantSurgeryRecord.doctor_id == current_user.id
    ).subquery()

    evolutions_7days = SurgeryEvolution.query.filter(
        SurgeryEvolution.evolution_type == '7_days',
        SurgeryEvolution.surgery_id.in_(surgery_ids_subq)
    ).all()
    evolutions_1year = SurgeryEvolution.query.filter(
        SurgeryEvolution.evolution_type == '1_year',
        SurgeryEvolution.surgery_id.in_(surgery_ids_subq)
    ).all()
    
    # Estatisticas por tipo de cirurgia
    all_surgeries = TransplantSurgeryRecord.query.filter_by(doctor_id=current_user.id).all()
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
            TransplantSurgeryRecord.doctor_id == current_user.id,
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

@app.route('/api/dashboard/one-year-second-surgery-patients', methods=['GET'])
@login_required
def dashboard_one_year_second_surgery_patients():
    if not current_user.is_doctor():
        return jsonify({'success': False, 'error': 'Apenas médicos'}), 403

    from models import SurgeryEvolution, TransplantSurgeryRecord, Patient

    rows = db.session.query(
        SurgeryEvolution.id.label('evolution_id'),
        SurgeryEvolution.evolution_date,
        TransplantSurgeryRecord.id.label('surgery_id'),
        TransplantSurgeryRecord.surgery_date,
        Patient.id.label('patient_id'),
        Patient.name.label('patient_name')
    ).join(
        TransplantSurgeryRecord, SurgeryEvolution.surgery_id == TransplantSurgeryRecord.id
    ).join(
        Patient, TransplantSurgeryRecord.patient_id == Patient.id
    ).filter(
        TransplantSurgeryRecord.doctor_id == current_user.id,
        SurgeryEvolution.evolution_type == '1_year',
        SurgeryEvolution.needs_another_surgery.is_(True)
    ).order_by(
        SurgeryEvolution.evolution_date.desc(),
        SurgeryEvolution.id.desc()
    ).all()

    seen_patients = set()
    patients = []
    for row in rows:
        if row.patient_id in seen_patients:
            continue
        seen_patients.add(row.patient_id)
        patients.append({
            'patient_id': row.patient_id,
            'patient_name': row.patient_name,
            'prontuario_url': url_for('prontuario', patient_id=row.patient_id),
            'surgery_id': row.surgery_id,
            'surgery_date': row.surgery_date.strftime('%d/%m/%Y') if row.surgery_date else None,
            'evolution_id': row.evolution_id,
            'evolution_date': row.evolution_date.strftime('%d/%m/%Y %H:%M') if row.evolution_date else None,
        })

    return jsonify({'success': True, 'total': len(patients), 'patients': patients})

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
        login_input = request.form.get('email', '').strip() # Mantendo o nome do campo como 'email' no form por enquanto
        password = request.form.get('password')
        
        # Busca por email ou usuário
        user = User.query.filter((User.email.ilike(login_input)) | (User.username == login_input)).first()
        
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
    from models import Indication, CosmeticProcedurePlan, HairTransplant, Procedure, Payment
    from collections import defaultdict
    
    # Buscar todas as indicações do médico
    notes = Note.query.filter_by(doctor_id=current_user.id).all()
    note_ids = [n.id for n in notes]
    
    procedures_completed = defaultdict(int)
    procedures_pending = defaultdict(int)
    
    # Contar indicações feitas vs planejadas
    if note_ids:
        # Optimized query for indications
        indications = Indication.query.filter(Indication.note_id.in_(note_ids)).all()
        for ind in indications:
            try:
                proc_name = ind.procedure.name if ind.procedure else 'Procedimento'
                if ind.performed:
                    procedures_completed[proc_name] += 1
                elif ind.indicated:
                    procedures_pending[proc_name] += 1
            except Exception:
                continue
    
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
    
    # Receita (apenas pagamentos pagos vinculados às consultas do médico)
    paid_payments = Payment.query.join(Appointment, Payment.appointment_id == Appointment.id).filter(
        Appointment.doctor_id == current_user.id,
        Payment.status == 'pago'
    )

    day_start = datetime.combine(today, datetime.min.time())
    day_end = datetime.combine(today, datetime.max.time())
    week_start = datetime.combine(monday, datetime.min.time())
    week_end = datetime.combine(sunday, datetime.max.time())
    month_start = datetime.combine(first_day, datetime.min.time())
    month_end = datetime.combine(last_day, datetime.max.time())

    payments_today = paid_payments.filter(Payment.paid_at >= day_start, Payment.paid_at <= day_end).all()
    payments_week = paid_payments.filter(Payment.paid_at >= week_start, Payment.paid_at <= week_end).all()
    payments_month = paid_payments.filter(Payment.paid_at >= month_start, Payment.paid_at <= month_end).all()

    receita_hoje = float(sum(float(p.total_amount or 0) for p in payments_today))
    receita_semana = float(sum(float(p.total_amount or 0) for p in payments_week))
    receita_mes = float(sum(float(p.total_amount or 0) for p in payments_month))
    ticket_medio = (receita_mes / len(payments_month)) if payments_month else 0

    # No-show (mês atual)
    agendados_mes_total = len(month_appointments)
    compareceram_mes = sum(1 for a in month_appointments if a.status == 'atendido')
    no_show_mes = sum(1 for a in month_appointments if a.status == 'faltou')
    taxa_no_show = (no_show_mes / agendados_mes_total * 100) if agendados_mes_total else 0

    # Pipeline de tratamentos
    indicados_pipeline = sum(procedures_completed.values()) + sum(procedures_pending.values())
    realizados_pipeline = sum(procedures_completed.values())
    pendentes_pipeline = sum(procedures_pending.values())
    valor_potencial = float(sum(float(plan.planned_value or 0) for plan in cosmetic_plans if not plan.was_performed))

    # Top receita por procedimento (pagamentos do mês)
    top_revenue = defaultdict(float)
    for payment in payments_month:
        for item in (payment.procedures or []):
            proc_name = item.get('name', 'Procedimento')
            if proc_name.lower().startswith('consulta'):
                continue
            try:
                top_revenue[proc_name] += float(item.get('value', 0) or 0)
            except (ValueError, TypeError):
                continue

    top_revenue_ordered = dict(sorted(top_revenue.items(), key=lambda x: x[1], reverse=True)[:5])

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
        # Receita
        'receita_hoje': receita_hoje,
        'receita_semana': receita_semana,
        'receita_mes': receita_mes,
        'ticket_medio': ticket_medio,
        # No-show
        'agendados_mes_total': agendados_mes_total,
        'compareceram_mes': compareceram_mes,
        'no_show_mes': no_show_mes,
        'taxa_no_show': taxa_no_show,
        # Pipeline
        'indicados_pipeline': indicados_pipeline,
        'realizados_pipeline': realizados_pipeline,
        'pendentes_pipeline': pendentes_pipeline,
        'valor_potencial': valor_potencial,
        # Top lucrativos
        'top_revenue': top_revenue_ordered,
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
            from datetime import datetime, date
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            # Forçar comparação direta de data no SQL para evitar problemas de fuso horário do servidor
            query = query.filter(
                db.cast(Appointment.start_time, db.Date) == target_date
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
        except (ValueError, TypeError):
            pass
    
    surgeries = surgery_query.all()
    
    events = []
    
    # ADICIONAR CIRURGIAS COMO EVENTOS NA AGENDA
    for surg in surgeries:
        try:
            from datetime import datetime
            surg_start_dt = datetime.combine(surg.date, surg.start_time)
            surg_end_dt = datetime.combine(surg.date, surg.end_time)
            start_iso = clinic_wall_time_iso(surg_start_dt)
            end_iso = clinic_wall_time_iso(surg_end_dt)
            
            # Tentar encontrar o paciente pelo nome para vincular o ID
            target_patient_id = None
            if surg.patient_name:
                patient_match = Patient.query.filter(Patient.name.ilike(surg.patient_name)).first()
                if patient_match:
                    target_patient_id = patient_match.id

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
                    'patientId': target_patient_id
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
            
            appointment_status = normalize_appointment_status(apt.status)

            # Use status color for border
            border_color = {
                'agendado': '#6c757d',
                'confirmado': '#0d6efd',
                'atendido': '#198754',
                'faltou': '#dc3545'
            }.get(appointment_status, '#6c757d')
            
            # Horários civis da agenda são interpretados no timezone da clínica.
            start_iso = clinic_wall_time_iso(apt.start_time)
            end_iso = clinic_wall_time_iso(apt.end_time)
            
            # Buscar código do paciente para este médico
            from models import PatientDoctor
            pd = PatientDoctor.query.filter_by(patient_id=apt.patient_id, doctor_id=apt.doctor_id).first()
            patient_code = pd.patient_code if pd else None
            
            # Buscar dados do paciente e médico com fallback em caso de erro
            patient_name = 'Paciente'
            patient_type = 'Particular'
            patient_phone = ''
            patient_cpf = ''
            patient_birth_date = ''
            patient_address = ''
            patient_city = ''
            patient_mother_name = ''
            patient_indication_source = ''
            patient_occupation = ''
            try:
                patient_name = apt.patient.name or 'Paciente'
                patient_type = apt.patient.patient_type or 'Particular'
                patient_phone = apt.patient.phone or ''
                patient_cpf = apt.patient.cpf or ''
                patient_birth_date = apt.patient.birth_date.isoformat() if apt.patient.birth_date else ''
                patient_address = apt.patient.address or ''
                patient_city = apt.patient.city or ''
                patient_mother_name = apt.patient.mother_name or ''
                patient_indication_source = apt.patient.indication_source or ''
                patient_occupation = apt.patient.occupation or ''
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
                'backgroundColor': '#0A66C2' if (apt.appointment_type or '') == 'Transplante Capilar' else doctor_color,
                'borderColor': border_color,
                'extendedProps': {
                    'status': appointment_status,
                    'appointmentType': apt.appointment_type or 'Particular',
                    'patientId': apt.patient_id,
                    'patientCode': patient_code,
                    'patientType': patient_type,
                    'doctorId': apt.doctor_id,
                    'doctorName': doctor_name,
                    'waiting': apt.waiting,
                    'checkedInTime': utc_instant_to_clinic_iso(apt.checked_in_time),
                    'phone': patient_phone,
                    'cpf': patient_cpf,
                    'birthDate': patient_birth_date,
                    'address': patient_address,
                    'city': patient_city,
                    'motherName': patient_mother_name,
                    'indicationSource': patient_indication_source,
                    'occupation': patient_occupation,
                    'notes': apt.notes or '',
                    'ivpStars': apt.patient.ivp_stars if apt.patient else None,
                    'statusCadastral': apt.patient.status_cadastral if apt.patient else 'ativo',
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
        
        results.append({
            'id': p.id,
            'name': p.name,
            'cpf': p.cpf or '',
            'prontuario': p.id,
            'last_consult': last_consult_date,
            'ivp_stars': p.ivp_stars
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
    try:
        appointment = Appointment.query.filter_by(id=appointment_id).first()
        if appointment is None:
            return jsonify({'success': False, 'error': 'Agendamento não encontrado'}), 404
        
        # Se médico, só pode deletar seus próprios
        if current_user.is_doctor() and appointment.doctor_id != current_user.id:
            return jsonify({'success': False, 'error': 'Não autorizado'}), 403
        
        # Deletar registros com FK NOT NULL (commercial_task)
        CommercialTask.query.filter_by(consultation_id=appointment_id).delete()
        
        # Desvincula registros com FK nullable (preserva os dados, apenas remove o vínculo)
        Evolution.query.filter_by(consultation_id=appointment_id).update({'consultation_id': None})
        Note.query.filter_by(appointment_id=appointment_id).update({'appointment_id': None})
        Payment.query.filter_by(appointment_id=appointment_id).update({'appointment_id': None})
        Prescription.query.filter_by(appointment_id=appointment_id).update({'appointment_id': None})
        
        db.session.delete(appointment)
        db.session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        app.logger.exception(f"Erro ao excluir agendamento {appointment_id}: {e}")
        return jsonify({
            'success': False,
            'error': 'Não foi possível excluir o agendamento. Tente novamente ou acione o suporte.'
        }), 500

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
    
    # Priorizar busca por ID se fornecido
    patient_id_input = data.get('patient_id')
    patient = None
    if patient_id_input:
        patient = Patient.query.get(patient_id_input)
    
    if not patient:
        # Fallback: Buscar por nome normalizado (case-insensitive) para evitar duplicatas
        patient_name_input = data.get('patientName', '').strip()
        if not patient_name_input:
            return jsonify({'success': False, 'error': 'patientName é obrigatório'}), 400
        patient = Patient.query.filter(db.func.lower(Patient.name) == db.func.lower(patient_name_input)).first()

    # Alerta de possível duplicidade: só ao criar paciente NOVO (sem patient_id
    # selecionado e sem correspondência exata), e somente se o usuário ainda não
    # confirmou criar mesmo assim (force_create). NÃO mescla/altera nada.
    if not patient and not patient_id_input and not data.get('force_create'):
        possible = find_possible_duplicate_patients(
            data.get('patientName', ''), doctor_id=doctor_id
        )
        if possible:
            return jsonify({
                'success': False,
                'warning': 'duplicate_found',
                'duplicates': possible,
                'message': 'Possível paciente já cadastrado. Deseja abrir a ficha existente ou criar um novo cadastro mesmo assim?'
            }), 409

    is_new_patient = False
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
            name=data.get('patientName', '').strip() or None,
            phone=phone_val,
            email=data.get('email', ''),
            cpf=cpf_val,
            birth_date=birth_date_val,
            address=address_val,
            city=city_val,
            mother_name=mother_name_val,
            indication_source=indication_source_val,
            occupation=occupation_val,
            patient_type=data.get('patientType', 'particular'),
            status_cadastral='provisorio',  # novo paciente nasce provisório
        )
        if not patient.name:
            return jsonify({'success': False, 'error': 'patientName é obrigatório'}), 400
        db.session.add(patient)
        db.session.flush()
        is_new_patient = True

        # Handle photo for new patient
        if 'photo_data' in data and data['photo_data']:
            try:
                save_patient_photo_data_url(patient, data['photo_data'])
            except Exception as e:
                app.logger.warning(f"Erro ao processar foto do paciente {patient.id}: {e}")
    else:
        # Paciente existente: atualizar dados se fornecidos
        if 'patientType' in data:
            patient.patient_type = data['patientType']
        if 'phone' in data and data['phone']:
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

    start_time = data.get('start')
    end_time = data.get('end')
    if not start_time or not end_time:
        return jsonify({'success': False, 'error': 'start e end são obrigatórios'}), 400

    appointment = Appointment(
        patient_id=patient.id,
        doctor_id=doctor_id,
        start_time=parse_datetime_with_tz(start_time),
        end_time=parse_datetime_with_tz(end_time),
        status=normalize_appointment_status(data.get('status')),
        appointment_type=data.get('appointmentType', 'Particular'),
        notes=data.get('notes', '')
    )

    db.session.add(appointment)
    db.session.flush()

    # Criar ou obter registro PatientDoctor.
    # Pacientes NOVOS (provisórios): sem patient_code — gerado somente na ativação manual.
    # Pacientes EXISTENTES (ativos): gerar código normalmente se ainda não tiver.
    pd = PatientDoctor.query.filter_by(patient_id=patient.id, doctor_id=doctor_id).first()
    if not pd:
        if is_new_patient:
            # Provisório: sem patient_code
            pd = PatientDoctor(patient_id=patient.id, doctor_id=doctor_id, patient_code=None)
        else:
            # Paciente ativo existente: garantir que tenha código
            next_code = generate_next_patient_code(doctor_id)
            pd = PatientDoctor(patient_id=patient.id, doctor_id=doctor_id, patient_code=next_code)
        db.session.add(pd)
    
    # Se for tipo de paciente Cirurgia, criar automaticamente no mapa cirúrgico
    surgery_created = False
    if data.get('patientType') == 'cirurgia' and data.get('surgery_name'):
        operating_room = OperatingRoom.query.first()
        if not operating_room:
            operating_room = OperatingRoom(name='Sala 1', capacity=1)
            db.session.add(operating_room)
            db.session.flush()
        
        start_dt = parse_datetime_with_tz(start_time)
        end_dt = parse_datetime_with_tz(end_time)
        
        surgery = Surgery(
            date=start_dt.date(),
            start_time=start_dt.time(),
            end_time=end_dt.time(),
            patient_id=patient.id,
            patient_name=patient.name,
            procedure_name=data.get('surgery_name', ''),
            doctor_id=doctor_id,
            operating_room_id=operating_room.id,
            status='agendada',
            notes=data.get('notes', ''),
            created_by=current_user.id
        )
        db.session.add(surgery)
        surgery_created = True
    
    db.session.commit()
    
    # === GOOGLE SHEETS: Agendamento de Cirurgia (Transplante Capilar) ===
    if data.get('appointmentType') == 'Transplante Capilar' and data.get('status', 'agendado') == 'agendado':
        try:
            from services.google_sheets import get_or_create_spreadsheet, _get_sheets_service
            import threading

            def _update_gs_surgery_date_thread(p_name, s_time):
                try:
                    spreadsheet_id = get_or_create_spreadsheet()
                    sheets = _get_sheets_service()
                    sheet_name = 'Transplante Capilar'
                    result = sheets.spreadsheets().values().get(
                        spreadsheetId=spreadsheet_id,
                        range=f'{sheet_name}!A:E'
                    ).execute()
                    values = result.get('values', [])
                    if not values: return
                    found_row_idx = -1
                    for i, row in enumerate(values):
                        if len(row) > 0 and row[0].strip().lower() == p_name.strip().lower():
                            found_row_idx = i + 1
                            break
                    if found_row_idx > 0:
                        update_range = f'{sheet_name}!D{found_row_idx}:E{found_row_idx}'
                        sheets.spreadsheets().values().update(
                            spreadsheetId=spreadsheet_id,
                            range=update_range,
                            valueInputOption='USER_ENTERED',
                            body={'values': [['agendado', s_time.strftime('%d/%m/%Y')]]}
                        ).execute()
                except Exception as e:
                    print(f"✗ Erro GS Surgery Update: {e}")

            threading.Thread(target=_update_gs_surgery_date_thread, args=(patient.name, appointment.start_time), daemon=True).start()
        except Exception as e:
            print(f"Erro ao iniciar thread GS: {e}")

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
    if 'consultation_date' in data:
        appointment.consultation_date = parse_datetime_with_tz(data['consultation_date']) if data['consultation_date'] else None
    if 'end' in data:
        appointment.end_time = parse_datetime_with_tz(data['end'])
    if 'status' in data:
        appointment.status = normalize_appointment_status(data['status'])
    if 'notes' in data:
        appointment.notes = data['notes']
    if 'appointment_type' in data:
        appointment.appointment_type = data['appointment_type']
    if 'appointmentType' in data:
        appointment.appointment_type = data['appointmentType']
    
    # === GOOGLE SHEETS: Atualização de Status/Data (Transplante Capilar) ===
    if appointment.appointment_type == 'Transplante Capilar' and appointment.status == 'agendado':
        try:
            from services.google_sheets import get_or_create_spreadsheet, _get_sheets_service
            import threading
            def _update_gs_status_thread(p_name, s_time):
                try:
                    spreadsheet_id = get_or_create_spreadsheet()
                    sheets = _get_sheets_service()
                    sheet_name = 'Transplante Capilar'
                    result = sheets.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=f'{sheet_name}!A:E').execute()
                    values = result.get('values', [])
                    if not values: return
                    for i, row in enumerate(values):
                        if len(row) > 0 and row[0].strip().lower() == p_name.strip().lower():
                            sheets.spreadsheets().values().update(
                                spreadsheetId=spreadsheet_id,
                                range=f'{sheet_name}!D{i+1}:E{i+1}',
                                valueInputOption='USER_ENTERED',
                                body={'values': [['agendado', s_time.strftime('%d/%m/%Y')]]}
                            ).execute()
                            break
                except Exception as e: print(f"✗ Erro GS Update: {e}")
            threading.Thread(target=_update_gs_status_thread, args=(appointment.patient.name, appointment.start_time), daemon=True).start()
        except Exception as e: print(f"Erro thread GS: {e}")
    if 'patient_type' in data:
        appointment.patient.patient_type = data['patient_type']
    if 'patientType' in data:
        appointment.patient.patient_type = data['patientType']
    
    # Cadastros provisórios são editados pela agenda, antes de existir prontuário real.
    # Para pacientes ativos, manter a proteção histórica e não alterar dados cadastrais aqui.
    patient_is_provisional = (
        appointment.patient and appointment.patient.status_cadastral == 'provisorio'
    )
    if patient_is_provisional:
        if 'phone' in data:
            appointment.patient.phone = data.get('phone') or None
        if 'cpf' in data:
            appointment.patient.cpf = data.get('cpf') or None
        if 'birth_date' in data:
            if data.get('birth_date'):
                from datetime import datetime
                appointment.patient.birth_date = datetime.strptime(data['birth_date'], '%Y-%m-%d').date()
            else:
                appointment.patient.birth_date = None
        if 'address' in data:
            appointment.patient.address = data.get('address') or None
        if 'city' in data:
            appointment.patient.city = data.get('city') or None
        if 'mother_name' in data:
            appointment.patient.mother_name = data.get('mother_name') or None
        if 'indication_source' in data:
            appointment.patient.indication_source = data.get('indication_source') or None
        if 'occupation' in data:
            appointment.patient.occupation = data.get('occupation') or None
    
    # Update patient photo if provided
    if 'photo_data' in data and data['photo_data']:
        try:
            save_patient_photo_data_url(appointment.patient, data['photo_data'])
        except Exception as e:
            app.logger.warning(
                f"Erro ao processar foto do paciente {appointment.patient.id}: {e}"
            )

    # Update patient name if provided.
    # Provisórios podem ter o cadastro corrigido diretamente na agenda.
    # Ativos preservam o comportamento legado de vincular por nome existente.
    if 'patientName' in data and data['patientName'] != appointment.patient.name:
        if patient_is_provisional:
            new_name = (data.get('patientName') or '').strip()
            if not new_name:
                return jsonify({'success': False, 'error': 'Nome do paciente é obrigatório'}), 400
            appointment.patient.name = new_name
        else:
            existing_patient = Patient.query.filter_by(name=data['patientName']).first()
            if existing_patient:
                appointment.patient_id = existing_patient.id
            else:
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
                photo_url = save_patient_photo(patient, file.read())
                db.session.commit()
                return jsonify({'success': True, 'photo_url': photo_url})
            except ValueError as e:
                db.session.rollback()
                return jsonify({'success': False, 'error': str(e)}), 400
            except Exception:
                db.session.rollback()
                app.logger.exception(f"Erro ao salvar foto do paciente {patient.id}")
                return jsonify({'success': False, 'error': 'Erro ao salvar foto'}), 500
    
    data = request.get_json(silent=True)
    if data and 'photo_data' in data:
        # Upload via base64 (webcam)
        try:
            photo_url = save_patient_photo_data_url(patient, data['photo_data'])
            db.session.commit()
            return jsonify({'success': True, 'photo_url': photo_url})
        except ValueError as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 400
        except Exception:
            db.session.rollback()
            app.logger.exception(f"Erro ao salvar foto do paciente {patient.id}")
            return jsonify({'success': False, 'error': 'Erro ao salvar foto'}), 500
            
    return jsonify({'success': False, 'error': 'Nenhuma foto fornecida'}), 400


@app.route('/api/patient/<int:patient_id>/photo/file', methods=['GET'])
@login_required
def get_patient_photo(patient_id):
    photo = PatientPhoto.query.filter_by(patient_id=patient_id).first_or_404()
    response = send_file(
        BytesIO(photo.data),
        mimetype=photo.mime_type,
        conditional=True,
        etag=True,
        max_age=3600,
    )
    response.headers['Cache-Control'] = 'private, max-age=3600'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response

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
            'patient_type': patient.patient_type or 'particular',
            'ivp_stars': patient.ivp_stars
        }
        
        # Se foi passado doctor_id válido, buscar código do paciente
        if doctor_id:
            pd = PatientDoctor.query.filter_by(patient_id=patient.id, doctor_id=doctor_id).first()
            patient_data['patient_code'] = pd.patient_code if pd else None
        
        result.append(patient_data)
    
    # Ordenar a lista de pacientes por código crescente (sem código vai ao fim)
    result.sort(key=lambda p: (p.get('patient_code') is None, p.get('patient_code') or 0))
    
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
        app.logger.debug(f"today-appointment: Encontrado appointment_id={appointment.id} para patient_id={patient_id}")
        return jsonify({'appointment_id': appointment.id})
    
    # Se nao encontrar pendente, buscar qualquer um de hoje
    appointment = Appointment.query.filter(
        Appointment.patient_id == patient_id,
        db.func.date(Appointment.start_time) == today
    ).order_by(Appointment.start_time.desc()).first()
    
    if appointment:
        app.logger.debug(f"today-appointment: Encontrado (qualquer) appointment_id={appointment.id} para patient_id={patient_id}")
        return jsonify({'appointment_id': appointment.id})
    
    app.logger.debug(f"today-appointment: Nenhum agendamento encontrado para patient_id={patient_id} em {today}")
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

        if not (current_user.is_doctor() or current_user.is_secretary()):
            return jsonify({'success': False, 'error': 'Sem permissão para editar anotações'}), 403

        if current_user.is_doctor():
            from models import PatientDoctor
            pd = PatientDoctor.query.filter_by(patient_id=note.patient_id, doctor_id=current_user.id).first()
            if not pd and not getattr(current_user, 'is_admin', lambda: False)():
                return jsonify({'success': False, 'error': 'Sem acesso a este paciente'}), 403

        data = request.get_json() or {}
        
        if 'content' in data:
            note.content = data['content']
        
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao atualizar nota: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/notes', methods=['POST'])
@login_required
def create_note():
    try:
        if not (current_user.is_doctor() or current_user.is_secretary()):
            return jsonify({'success': False, 'error': 'Sem permissão'}), 403

        data = request.get_json() or {}
        patient_id = data.get('patient_id')
        appointment_id = data.get('appointment_id')
        note_type = data.get('note_type')
        content = data.get('content', '')

        if not patient_id or not note_type:
            return jsonify({'success': False, 'error': 'patient_id e note_type são obrigatórios'}), 400

        if current_user.is_doctor():
            from models import PatientDoctor
            pd = PatientDoctor.query.filter_by(patient_id=patient_id, doctor_id=current_user.id).first()
            if not pd and not getattr(current_user, 'is_admin', lambda: False)():
                return jsonify({'success': False, 'error': 'Sem acesso a este paciente'}), 403

        note = Note(
            patient_id=patient_id,
            doctor_id=current_user.id,
            appointment_id=appointment_id,
            note_type=note_type,
            content=content
        )
        db.session.add(note)
        db.session.commit()

        return jsonify({'success': True, 'id': note.id})
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao criar nota: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/agenda/export/pdf', methods=['GET'])
@login_required
def export_agenda_pdf():
    """Exporta agenda em PDF"""
    from utils.exports.pdf_export import PDFExporter
    
    start_date = request.args.get('start', clinic_today().isoformat())
    end_date = request.args.get('end', clinic_today().isoformat())
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
    
    start_date = request.args.get('start', clinic_today().isoformat())
    end_date = request.args.get('end', clinic_today().isoformat())
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
    if not current_user.is_doctor() and not current_user.is_secretary():
        return jsonify({'success': False, 'error': 'Sem permissão'}), 403
    
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

    # Secretárias: priorizar DP quando existir, mas manter acesso ao histórico geral
    # mesmo sem vínculo PatientDoctor (garante visão para todas as 3 secretárias).
    if current_user.is_secretary():
        from models import PatientDoctor
        pd = PatientDoctor.query.filter_by(patient_id=patient_id).first()
        if pd:
            from services.authz import can_view_dp
            if can_view_dp(pd):
                return redirect(url_for('prontuario_dp', dp_id=pd.id))
        # Sem vínculo DP válido: continuar para o prontuário padrão com histórico.

    # Médicos CP: criar/obter dp e redirecionar para rota dp
    if current_user.role_clinico == 'CP':
        _patient_check = Patient.query.get(patient_id)
        if _patient_check and _patient_check.status_cadastral == 'provisorio':
            flash('Cadastro provisório — solicite ativação à secretária antes de abrir o prontuário.', 'warning')
            return redirect(url_for('agenda'))
        from models import PatientDoctor as _PD
        _dp = _PD.query.filter_by(patient_id=patient_id, doctor_id=current_user.id).first()
        if not _dp:
            next_code = generate_next_patient_code(current_user.id)
            _dp = _PD(patient_id=patient_id, doctor_id=current_user.id, patient_code=next_code)
            db.session.add(_dp)
            db.session.commit()
        return redirect(url_for('prontuario_dp', dp_id=_dp.id))

    try:
        # DERM: Verificar acesso: Médicos veem apenas seus próprios pacientes
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
        from models import Note, Indication, CosmeticProcedurePlan, HairTransplant, TransplantImage
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
            
            # Forçar carregamento de dados relacionados
            all_cosmetic_plans = []
            seen_cosmetic_plan_ids = set()
            for note in appt_notes:
                for plan in note.cosmetic_plans:
                    if plan.id in seen_cosmetic_plan_ids:
                        continue
                    seen_cosmetic_plan_ids.add(plan.id)
                    all_cosmetic_plans.append({
                        'id': plan.id,
                        'name': plan.name,
                        'procedure_name': plan.procedure_name,
                        'planned_value': plan.planned_value,
                        'final_budget': plan.final_budget,
                        'was_performed': plan.was_performed,
                        'performed_date': plan.performed_date,
                        'follow_up_months': plan.follow_up_months
                    })
            
            # Separar notas por tipo (preferir nota com conteúdo não-vazio)
            notes_by_type = {}
            for _n in appt_notes:
                existing = notes_by_type.get(_n.note_type)
                if existing is None or ((_n.content or '').strip() and not (existing.content or '').strip()):
                    notes_by_type[_n.note_type] = _n
            
            # Identificar consulta finalizada
            is_finalized, finalized_note = _resolve_consultation_finalization(
                db.session.get(Appointment, appt_id),
                appt_notes
            )
            
            # Usar dados da primeira nota como referência
            first_note = sorted(appt_notes, key=lambda x: x.created_at)[0]
            
            # Obter appointment para pegar a data correta
            appointment = db.session.get(Appointment, appt_id)
            if appointment:
                consultation_date = appointment.consultation_date or appointment.start_time
            else:
                consultation_date = (finalized_note.created_at if finalized_note else first_note.created_at)
            
            consultations.append({
                'id': appt_id,
                'date': consultation_date,
                'doctor': first_note.doctor,
                'duration': finalized_note.consultation_duration if finalized_note else None,
                'category': finalized_note.category if finalized_note else first_note.category,
                'notes_by_type': notes_by_type,
                'all_notes': appt_notes,
                'cosmetic_plans': all_cosmetic_plans,
                'is_finalized': is_finalized
            })
        
        # FALLBACK: Agrupar notas SEM appointment_id
        notes_without_appointment.sort(key=lambda x: x.created_at, reverse=True)
        for note in notes_without_appointment:
            if note.id in processed_notes:
                continue
            
            window_start = note.created_at - timedelta(seconds=2)
            window_end = note.created_at + timedelta(seconds=2)
            
            grouped_notes = [n for n in notes_without_appointment
                            if n.id not in processed_notes
                            and n.doctor_id == note.doctor_id
                            and window_start <= n.created_at <= window_end]
            
            for gn in grouped_notes:
                processed_notes.add(gn.id)
            
            all_cosmetic_plans = []
            seen_cosmetic_plan_ids = set()
            for gn in grouped_notes:
                for plan in gn.cosmetic_plans:
                    if plan.id in seen_cosmetic_plan_ids:
                        continue
                    seen_cosmetic_plan_ids.add(plan.id)
                    all_cosmetic_plans.append({
                        'id': plan.id,
                        'name': plan.name,
                        'procedure_name': plan.procedure_name,
                        'planned_value': plan.planned_value,
                        'final_budget': plan.final_budget,
                        'was_performed': plan.was_performed,
                        'performed_date': plan.performed_date,
                        'follow_up_months': plan.follow_up_months
                    })
            
            notes_by_type = {}
            for _gn in grouped_notes:
                existing = notes_by_type.get(_gn.note_type)
                if existing is None or ((_gn.content or '').strip() and not (existing.content or '').strip()):
                    notes_by_type[_gn.note_type] = _gn
            is_finalized, finalized_note = _resolve_consultation_finalization(None, grouped_notes)
            
            consultations.append({
                'id': note.id,
                'date': note.created_at,
                'doctor': note.doctor,
                'duration': finalized_note.consultation_duration if finalized_note else None,
                'category': note.category,
                'notes_by_type': notes_by_type,
                'all_notes': grouped_notes,
                'cosmetic_plans': all_cosmetic_plans,
                'is_finalized': is_finalized
            })
        
        # Incluir agendamentos "atendido" sem notas
        covered_appt_ids = {c['id'] for c in consultations}
        empty_q = Appointment.query.filter(
            Appointment.patient_id == patient_id,
            Appointment.status == 'atendido'
        )
        if covered_appt_ids:
            empty_q = empty_q.filter(~Appointment.id.in_(list(covered_appt_ids)))
        empty_appts = empty_q.all()
        for ea in empty_appts:
            ea_date = ea.consultation_date or ea.start_time
            consultations.append({
                'id': ea.id,
                'date': ea_date,
                'doctor': ea.doctor,
                'duration': None,
                'category': ea.appointment_type or 'Consulta',
                'notes_by_type': {},
                'all_notes': [],
                'cosmetic_plans': [],
                'is_finalized': bool(getattr(ea, 'is_finalized', False) or getattr(ea, 'finalized_at', None)),
                'status': ea.status
            })

        consultations.sort(key=lambda x: x['date'], reverse=True)
        
        # TRATAMENTO SEGURO DO APPOINTMENT_ID DA URL
        appointment_id = request.args.get('appointment_id', type=int)
        active_appt = None
        appointment_start_iso = None
        if appointment_id:
            active_appt = db.session.get(Appointment, appointment_id)
            if active_appt and active_appt.patient_id == patient_id:
                effective_dt = active_appt.consultation_date or active_appt.start_time
                if effective_dt:
                    appointment_start_iso = effective_dt.strftime('%Y-%m-%dT%H:%M')
            else:
                appointment_id = None # Anular se inválido ou de outro paciente
                active_appt = None

        patient_type_label = (patient.patient_type or 'particular')
        if isinstance(patient_type_label, str) and patient_type_label.lower() == 'particular':
            patient_type_label = 'Particular'

        consultation_type_label = None
        if active_appt and active_appt.appointment_type:
            consultation_type_label = active_appt.appointment_type
        elif consultations:
            latest_category = consultations[0].get('category')
            if latest_category:
                consultation_type_label = str(latest_category).replace('_', ' ').title()
        if not consultation_type_label:
            consultation_type_label = 'Não informado'

        age = None
        if patient.birth_date:
            today = clinic_today()
            age = today.year - patient.birth_date.year - ((today.month, today.day) < (patient.birth_date.month, patient.birth_date.day))
        
        # TIMELINE REFACTOR
        debug_mode = request.args.get('debug') == '1'
        timeline_events = build_patient_timeline(patient_id)
        
        debug_info = None
        if debug_mode:
            debug_info = {'events_total': len(timeline_events)}

        return render_template('prontuario.html', 
                             patient=patient, 
                             procedures=procedures,
                             tags=tags,
                             patient_tags=patient_tags,
                             notes=notes,
                             consultations=consultations,
                             appointment_id=appointment_id,
                             appointment_start_iso=appointment_start_iso,
                             patient_type_label=patient_type_label,
                             consultation_type_label=consultation_type_label,
                             age=age,
                             timeline_events=timeline_events,
                             debug_info=debug_info)
    except Exception as e:
        import traceback
        print(f"ERRO PRONTUARIO (Patient: {patient_id}, Appt: {request.args.get('appointment_id')}): {str(e)}")
        print(traceback.format_exc())
        return "Internal Server Error", 500

@app.route('/prontuario/dp/<int:dp_id>')
@login_required
def prontuario_dp(dp_id):
    from services.authz import require_dp_view, can_edit_dp
    from models import PlasticSurgeryEncounter

    dp = require_dp_view(dp_id)
    patient = Patient.query.get_or_404(dp.patient_id)
    # Secretárias agora podem editar para preencher triagem/orçamento
    read_only = not can_edit_dp(dp)

    doctor = db.session.get(User, dp.doctor_id)

    use_cp = False
    if doctor and doctor.role_clinico == 'CP':
        use_cp = True
    elif not current_user.is_secretary() and current_user.role_clinico == 'CP':
        use_cp = True

    age = None
    if patient.birth_date:
        today = clinic_today()
        age = today.year - patient.birth_date.year - (
            (today.month, today.day) < (patient.birth_date.month, patient.birth_date.day)
        )

    imc = None
    imc_status = None
    if patient.weight and patient.height and patient.height > 0:
        h_m = patient.height / 100.0
        imc = round(patient.weight / (h_m * h_m), 1)
        if imc < 18.5:
            imc_status = 'Abaixo do peso'
        elif imc < 25:
            imc_status = 'Normal'
        elif imc < 30:
            imc_status = 'Sobrepeso'
        else:
            imc_status = 'Obesidade'

    if use_cp:
        last_encounter = PlasticSurgeryEncounter.query\
            .filter_by(doctor_patient_id=dp.id)\
            .order_by(PlasticSurgeryEncounter.updated_at.desc())\
            .first()
        return render_template(
            'prontuario_cp.html',
            dp=dp,
            patient=patient,
            doctor=doctor,
            read_only=read_only,
            age=age,
            imc=imc,
            imc_status=imc_status,
            last_encounter=last_encounter,
            current_user=current_user
        )
    else:
        from datetime import timedelta
        from collections import defaultdict
        procedures = Procedure.query.all()
        tags = Tag.query.all()
        patient_tags = [pt.tag_id for pt in patient.tags]
        notes = Note.query.filter_by(patient_id=patient.id)\
            .options(
                db.joinedload(Note.indications).joinedload(Indication.procedure),
                db.joinedload(Note.cosmetic_plans),
                db.joinedload(Note.hair_transplants).joinedload(HairTransplant.images)
            )\
            .order_by(Note.created_at.desc())\
            .all()

        consultations = []
        processed_notes = set()
        notes_by_appointment = defaultdict(list)
        notes_without_appointment = []
        for note in notes:
            if note.appointment_id:
                notes_by_appointment[note.appointment_id].append(note)
            else:
                notes_without_appointment.append(note)

        for appt_id, appt_notes in notes_by_appointment.items():
            for note in appt_notes:
                processed_notes.add(note.id)
            all_cosmetic_plans = []
            seen_cosmetic_plan_ids = set()
            for note in appt_notes:
                for plan in note.cosmetic_plans:
                    if plan.id in seen_cosmetic_plan_ids:
                        continue
                    seen_cosmetic_plan_ids.add(plan.id)
                    all_cosmetic_plans.append({
                        'id': plan.id,
                        'name': plan.name,
                        'procedure_name': plan.procedure_name,
                        'planned_value': plan.planned_value,
                        'final_budget': plan.final_budget,
                        'was_performed': plan.was_performed,
                        'performed_date': plan.performed_date,
                        'follow_up_months': plan.follow_up_months
                    })
            notes_by_type = {}
            for _n in appt_notes:
                existing = notes_by_type.get(_n.note_type)
                if existing is None or ((_n.content or '').strip() and not (existing.content or '').strip()):
                    notes_by_type[_n.note_type] = _n
            appointment = db.session.get(Appointment, appt_id)
            is_finalized, finalized_note = _resolve_consultation_finalization(appointment, appt_notes)
            first_note = sorted(appt_notes, key=lambda x: x.created_at)[0]
            if appointment:
                consultation_date = appointment.consultation_date or appointment.start_time
            else:
                consultation_date = finalized_note.created_at if finalized_note else first_note.created_at
            consultations.append({
                'id': appt_id,
                'date': consultation_date,
                'doctor': first_note.doctor,
                'duration': finalized_note.consultation_duration if finalized_note else None,
                'category': finalized_note.category if finalized_note else first_note.category,
                'notes_by_type': notes_by_type,
                'all_notes': appt_notes,
                'cosmetic_plans': all_cosmetic_plans,
                'is_finalized': is_finalized
            })

        notes_without_appointment.sort(key=lambda x: x.created_at, reverse=True)
        for note in notes_without_appointment:
            if note.id in processed_notes:
                continue
            window_start = note.created_at - timedelta(seconds=2)
            window_end = note.created_at + timedelta(seconds=2)
            grouped_notes = [n for n in notes_without_appointment
                            if n.id not in processed_notes
                            and n.doctor_id == note.doctor_id
                            and window_start <= n.created_at <= window_end]
            for gn in grouped_notes:
                processed_notes.add(gn.id)
            all_cosmetic_plans = []
            seen_cosmetic_plan_ids = set()
            for gn in grouped_notes:
                for plan in gn.cosmetic_plans:
                    if plan.id in seen_cosmetic_plan_ids:
                        continue
                    seen_cosmetic_plan_ids.add(plan.id)
                    all_cosmetic_plans.append({
                        'id': plan.id,
                        'name': plan.name,
                        'procedure_name': plan.procedure_name,
                        'planned_value': plan.planned_value,
                        'final_budget': plan.final_budget,
                        'was_performed': plan.was_performed,
                        'performed_date': plan.performed_date,
                        'follow_up_months': plan.follow_up_months
                    })
            notes_by_type = {}
            for _gn in grouped_notes:
                existing = notes_by_type.get(_gn.note_type)
                if existing is None or ((_gn.content or '').strip() and not (existing.content or '').strip()):
                    notes_by_type[_gn.note_type] = _gn
            is_finalized, finalized_note = _resolve_consultation_finalization(None, grouped_notes)
            consultations.append({
                'id': note.id,
                'date': note.created_at,
                'doctor': note.doctor,
                'duration': finalized_note.consultation_duration if finalized_note else None,
                'category': note.category,
                'notes_by_type': notes_by_type,
                'all_notes': grouped_notes,
                'cosmetic_plans': all_cosmetic_plans,
                'is_finalized': is_finalized
            })

        consultations.sort(key=lambda x: x['date'], reverse=True)
        timeline_events = build_patient_timeline(patient.id)
        return render_template(
            'prontuario.html',
            patient=patient,
            procedures=procedures,
            tags=tags,
            patient_tags=patient_tags,
            notes=notes,
            consultations=consultations,
            appointment_id=None,
            appointment_start_iso=None,
            age=age,
            timeline_events=timeline_events,
            debug_info=None,
            read_only=read_only,
            dp=dp
        )


@app.route('/api/doctor-patients/search')
@login_required
def search_doctor_patients():
    q = request.args.get('q', '').strip()
    doctor_id = request.args.get('doctor_id')
    if not q or len(q) < 2:
        return jsonify([])

    from models import PatientDoctor

    digits = ''.join(ch for ch in q if ch.isdigit())

    def only_digits_expr(column):
        expr = db.func.coalesce(column, '')
        for char in ['(', ')', '-', '.', '/', ' ']:
            expr = db.func.replace(expr, char, '')
        return expr

    search_filters = [
        Patient.name.ilike(f'%{q}%'),
        Patient.phone.ilike(f'%{q}%'),
        Patient.cpf.ilike(f'%{q}%'),
    ]
    if digits:
        search_filters.extend([
            only_digits_expr(Patient.phone).ilike(f'%{digits}%'),
            only_digits_expr(Patient.cpf).ilike(f'%{digits}%'),
        ])
        try:
            search_filters.append(PatientDoctor.patient_code == int(digits))
        except ValueError:
            pass

    base_q = db.session.query(PatientDoctor, Patient, User)\
        .join(Patient, PatientDoctor.patient_id == Patient.id)\
        .join(User, PatientDoctor.doctor_id == User.id)\
        .filter(db.or_(*search_filters))

    if doctor_id and doctor_id != 'null':
        try:
            doctor_id = int(doctor_id)
            base_q = base_q.filter(PatientDoctor.doctor_id == doctor_id)
        except (TypeError, ValueError):
            pass

    if not (current_user.is_secretary() or current_user.role_clinico in ('SECRETARY', 'ADMIN')):
        base_q = base_q.filter(PatientDoctor.doctor_id == current_user.id)

    # Ordenar por código do paciente crescente
    base_q = base_q.order_by(PatientDoctor.patient_code.asc())

    rows = base_q.limit(20).all()

    result = []
    for dp, patient, doctor in rows:
        result.append({
            'dp_id': dp.id,
            'patient_id': patient.id,
            'patient_name': patient.name,
            'patient_phone': patient.phone or '',
            'patient_cpf': patient.cpf or '',
            'patient_code': dp.patient_code,
            'doctor_id': doctor.id,
            'doctor_name': doctor.name,
            'doctor_role': doctor.role_clinico or 'DERM',
        })

    return jsonify(result)


@app.route('/api/doctor-patients/link', methods=['POST'])
@login_required
def link_doctor_patient():
    if not (current_user.is_secretary() or current_user.role_clinico in ('SECRETARY', 'ADMIN')):
        abort(403)

    data = request.get_json() or {}
    patient_id = data.get('patient_id')
    doctor_id = data.get('doctor_id')

    if not patient_id or not doctor_id:
        return jsonify({'error': 'patient_id e doctor_id obrigatórios'}), 400

    from models import PatientDoctor

    _p = Patient.query.get(patient_id)
    if _p and _p.status_cadastral == 'provisorio':
        return jsonify({'error': 'Paciente provisório. Use o endpoint de ativação (/api/patients/<id>/ativar).'}), 400

    dp = PatientDoctor.query.filter_by(patient_id=patient_id, doctor_id=doctor_id).first()
    if not dp:
        next_code = generate_next_patient_code(doctor_id)
        dp = PatientDoctor(
            patient_id=patient_id,
            doctor_id=doctor_id,
            patient_code=next_code
        )
        db.session.add(dp)
        db.session.commit()

    return jsonify({'dp_id': dp.id, 'patient_code': dp.patient_code})


def _activation_warnings_for(provisional, doctor_id, phone_value=None, cpf_value=None):
    warnings = []

    name_dups = find_possible_duplicate_patients(provisional.name, doctor_id=doctor_id)
    name_dups = [d for d in name_dups if d['id'] != provisional.id]
    if name_dups:
        warnings.extend([{**d, 'reason': 'nome_semelhante'} for d in name_dups])

    cpf_to_check = cpf_value or provisional.cpf
    if cpf_to_check:
        cpf_dups = Patient.query.filter(
            Patient.cpf == cpf_to_check,
            Patient.id != provisional.id,
            Patient.status_cadastral == 'ativo'
        ).all()
        for p in cpf_dups:
            if not any(w['id'] == p.id for w in warnings):
                warnings.append({'id': p.id, 'name': p.name, 'reason': 'mesmo_cpf',
                                 'phone': p.phone, 'cpf': p.cpf})

    phone_to_check = phone_value or provisional.phone
    if phone_to_check:
        phone_dups = Patient.query.filter(
            Patient.phone == phone_to_check,
            Patient.id != provisional.id,
            Patient.status_cadastral == 'ativo'
        ).all()
        for p in phone_dups:
            if not any(w['id'] == p.id for w in warnings):
                warnings.append({'id': p.id, 'name': p.name, 'reason': 'mesmo_telefone',
                                 'phone': p.phone, 'cpf': p.cpf})

    return warnings


def _activation_required_errors(provisional, phone_input='', cpf_input=''):
    errors = []
    if not (phone_input or provisional.phone):
        errors.append({
            'field': 'phone',
            'error': 'phone_required',
            'message': 'Telefone obrigatório. Por favor, informe o telefone do paciente antes de ativar.'
        })
    if not (cpf_input or provisional.cpf):
        errors.append({
            'field': 'cpf',
            'error': 'cpf_required',
            'message': 'CPF obrigatório. Por favor, informe o CPF do paciente antes de ativar.'
        })
    return errors


@app.route('/api/patients/<int:patient_id>/activation-preview', methods=['POST'])
@login_required
def preview_ativacao_paciente(patient_id):
    """Verifica requisitos e duplicidades da ativação sem alterar o cadastro."""
    if not (current_user.is_doctor() or current_user.is_secretary()
            or current_user.role_clinico in ('SECRETARY', 'ADMIN')):
        abort(403)

    data = request.get_json() or {}
    doctor_id = data.get('doctor_id')
    if current_user.is_doctor():
        doctor_id = current_user.id
    if not doctor_id:
        return jsonify({'error': 'doctor_id obrigatório'}), 400

    provisional = Patient.query.get(patient_id)
    if not provisional:
        return jsonify({'error': 'Paciente não encontrado'}), 404
    if provisional.status_cadastral != 'provisorio':
        return jsonify({'error': 'Paciente já está ativo', 'patient_id': provisional.id}), 409

    phone_input = (data.get('phone') or '').strip()
    cpf_input = (data.get('cpf') or '').strip()
    required_errors = _activation_required_errors(provisional, phone_input, cpf_input)
    if required_errors:
        return jsonify({
            'success': False,
            'error': 'required_fields',
            'required': required_errors,
            'message': 'Telefone e CPF são obrigatórios para ativar o cadastro provisório.'
        }), 400

    warnings = _activation_warnings_for(provisional, doctor_id, phone_input, cpf_input)
    if warnings:
        return jsonify({
            'success': False,
            'warning': 'duplicates_found',
            'warnings': warnings,
            'message': 'Possíveis cadastros duplicados encontrados. Revise antes de ativar.'
        }), 409

    return jsonify({
        'success': True,
        'warnings': [],
        'message': ''
    })


@app.route('/api/patients/<int:patient_id>/ativar', methods=['POST'])
@login_required
def ativar_paciente(patient_id):
    """Converte cadastro PROVISORIO em ATIVO e gera patient_code.

    Payload JSON:
      - doctor_id (int, obrigatório)
      - merge_into_patient_id (int, opcional): se informado, transfere os
        agendamentos do provisório para o paciente ativo existente e descarta
        o provisório; caso contrário, ativa o próprio cadastro provisório.
      - phone (str, obrigatório se o provisório ainda não tiver telefone)
      - cpf (str, obrigatório se o provisório ainda não tiver CPF)
      - force (bool, opcional): confirmar mesmo havendo alertas de duplicidade.

    Retorna:
      - activated_patient_id: ID do paciente definitivo resultante
      - patient_code: código gerado
      - action: 'activate' | 'merge'
      - warnings: lista de possíveis duplicados (se force não informado)
    """
    if not (current_user.is_doctor() or current_user.is_secretary()
            or current_user.role_clinico in ('SECRETARY', 'ADMIN')):
        abort(403)

    data = request.get_json() or {}
    doctor_id = data.get('doctor_id')
    merge_into_id = data.get('merge_into_patient_id')
    force = bool(data.get('force', False))

    if current_user.is_doctor():
        doctor_id = current_user.id

    if not doctor_id:
        return jsonify({'error': 'doctor_id obrigatório'}), 400

    provisional = Patient.query.get(patient_id)
    if not provisional:
        return jsonify({'error': 'Paciente não encontrado'}), 404
    if provisional.status_cadastral != 'provisorio':
        return jsonify({'error': 'Paciente já está ativo', 'patient_id': provisional.id}), 409

    # --- Telefone e CPF obrigatórios para ativar ---
    phone_input = (data.get('phone') or '').strip()
    cpf_input = (data.get('cpf') or '').strip()
    required_errors = _activation_required_errors(provisional, phone_input, cpf_input)
    if required_errors:
        return jsonify({
            'success': False,
            'error': 'required_fields',
            'required': required_errors,
            'message': 'Telefone e CPF são obrigatórios para ativar o cadastro provisório.'
        }), 400
    if phone_input:
        provisional.phone = phone_input
    if cpf_input:
        provisional.cpf = cpf_input
    if phone_input or cpf_input:
        db.session.flush()

    # --- Alertas de duplicidade (antes de forçar) ---
    if not force:
        warnings = _activation_warnings_for(provisional, doctor_id, phone_input, cpf_input)
        if warnings:
            return jsonify({
                'success': False,
                'warning': 'duplicates_found',
                'warnings': warnings,
                'message': 'Possíveis cadastros duplicados encontrados. Revise antes de ativar.'
            }), 409

    try:
        if merge_into_id:
            # --- MERGE: transferir agendamentos do provisório para ativo existente ---
            target = Patient.query.get(merge_into_id)
            if not target:
                return jsonify({'error': 'Paciente destino não encontrado'}), 404
            if target.status_cadastral != 'ativo':
                return jsonify({'error': 'Paciente destino também é provisório'}), 400

            from models import (Note, Evolution, Surgery, TransplantSurgeryRecord,
                                FollowUpReminder, Prescription, Payment,
                                PatientTag, PatientFunnelStatus, ProcedureRecord)
            TRANSFERABLE = [Appointment, Note, Evolution, Surgery,
                            TransplantSurgeryRecord, FollowUpReminder, Prescription,
                            Payment, PatientTag, ProcedureRecord]
            for cls in TRANSFERABLE:
                cls.query.filter_by(patient_id=provisional.id).update(
                    {'patient_id': target.id}, synchronize_session=False
                )
            # CommercialTask tem FK NOT NULL para consultation_id — apenas reatribui patient_id
            from models import CommercialTask
            CommercialTask.query.filter_by(patient_id=provisional.id).update(
                {'patient_id': target.id}, synchronize_session=False
            )
            # Remover PatientDoctor do provisório (sem código) e apagar provisório
            PatientDoctor.query.filter_by(patient_id=provisional.id).delete()
            db.session.delete(provisional)

            # Garantir que o ativo tenha PatientDoctor com código
            pd = PatientDoctor.query.filter_by(patient_id=target.id, doctor_id=doctor_id).first()
            if not pd:
                next_code = generate_next_patient_code(doctor_id)
                pd = PatientDoctor(patient_id=target.id, doctor_id=doctor_id,
                                   patient_code=next_code)
                db.session.add(pd)
            elif pd.patient_code is None:
                pd.patient_code = generate_next_patient_code(doctor_id)

            db.session.flush()
            log = PatientActivationLog(
                provisional_patient_id=patient_id,
                activated_patient_id=target.id,
                action='merge',
                performed_by_user_id=current_user.id,
                doctor_id=doctor_id,
                patient_code_assigned=pd.patient_code,
            )
            db.session.add(log)
            db.session.commit()
            return jsonify({
                'success': True,
                'action': 'merge',
                'activated_patient_id': target.id,
                'patient_code': pd.patient_code,
            })

        else:
            # --- ATIVAR: promover o próprio provisório a ativo ---
            provisional.status_cadastral = 'ativo'

            pd = PatientDoctor.query.filter_by(
                patient_id=provisional.id, doctor_id=doctor_id
            ).first()
            if not pd:
                next_code = generate_next_patient_code(doctor_id)
                pd = PatientDoctor(patient_id=provisional.id, doctor_id=doctor_id,
                                   patient_code=next_code)
                db.session.add(pd)
            elif pd.patient_code is None:
                pd.patient_code = generate_next_patient_code(doctor_id)

            db.session.flush()
            log = PatientActivationLog(
                provisional_patient_id=patient_id,
                activated_patient_id=provisional.id,
                action='activate',
                performed_by_user_id=current_user.id,
                doctor_id=doctor_id,
                patient_code_assigned=pd.patient_code,
            )
            db.session.add(log)
            db.session.commit()
            return jsonify({
                'success': True,
                'action': 'activate',
                'activated_patient_id': provisional.id,
                'patient_code': pd.patient_code,
            })

    except Exception as e:
        db.session.rollback()
        app.logger.exception('Erro ao ativar paciente %s', patient_id)
        return jsonify({'error': str(e)}), 500


@app.route('/api/reports/patient-growth')
@login_required
def report_patient_growth():
    """Relatório gerencial de crescimento de pacientes (somente leitura).

    Estrutura preparada para uso futuro. Retorna:
      - monthly: novos pacientes por mês (YYYY-MM)
      - annual: novos pacientes por ano
      - total: total acumulado de pacientes cadastrados

    Pode ser filtrado por médico via ?doctor_id=. Quando informado, usa a data
    de vínculo (patient_doctor.created_at); sem filtro, usa patient.created_at.
    """
    doctor_id = request.args.get('doctor_id')

    if doctor_id and doctor_id not in ('null', ''):
        try:
            doctor_id = int(doctor_id)
        except (TypeError, ValueError):
            doctor_id = None
    else:
        doctor_id = None

    if doctor_id:
        created_col = PatientDoctor.created_at
        base = db.session.query(created_col).filter(PatientDoctor.doctor_id == doctor_id)
    else:
        created_col = Patient.created_at
        base = db.session.query(created_col)

    rows = base.filter(created_col.isnot(None)).all()

    monthly = {}
    annual = {}
    for (created,) in rows:
        if not created:
            continue
        ym = created.strftime('%Y-%m')
        y = created.strftime('%Y')
        monthly[ym] = monthly.get(ym, 0) + 1
        annual[y] = annual.get(y, 0) + 1

    monthly_list = [{'period': k, 'count': monthly[k]} for k in sorted(monthly)]
    annual_list = [{'year': k, 'count': annual[k]} for k in sorted(annual)]

    return jsonify({
        'monthly': monthly_list,
        'annual': annual_list,
        'total': sum(annual.values()),
        'doctor_id': doctor_id,
    })


def _audit_access_required():
    if not (current_user.is_doctor() or current_user.is_secretary() or
            current_user.role_clinico in ('SECRETARY', 'ADMIN')):
        abort(403)


@app.route('/admin/audit-patients')
@login_required
def audit_patients_page():
    """Tela de auditoria de pacientes antigos (duplicados/possíveis problemas) — somente leitura."""
    _audit_access_required()
    return render_template('admin/audit_patients.html')


@app.route('/api/admin/audit-patients')
@login_required
def api_audit_patients():
    """
    Relatório de auditoria de pacientes antigos (FASE 2). Somente leitura.
    Retorna pacientes com possíveis problemas para revisão manual.
    NÃO mescla, exclui ou altera nenhum paciente.
    """
    _audit_access_required()
    from difflib import SequenceMatcher
    from collections import defaultdict

    # ── 1. Coleta agregada de todos os pacientes com contadores ──
    sql = """
    SELECT
        p.id,
        p.name,
        p.phone,
        p.cpf,
        p.city,
        p.created_at,
        pd.id AS pd_id,
        pd.doctor_id,
        pd.patient_code,
        u.name AS doctor_name,
        (SELECT COUNT(*) FROM appointment a WHERE a.patient_id = p.id) AS count_appointments,
        (SELECT COUNT(*) FROM note n WHERE n.patient_id = p.id) AS count_notes,
        (SELECT COUNT(*) FROM evolution e WHERE e.patient_id = p.id) AS count_evolutions,
        (SELECT COUNT(*) FROM surgery s WHERE s.patient_id = p.id) AS count_surgeries,
        (SELECT COUNT(*) FROM transplant_surgery_record tsr WHERE tsr.patient_id = p.id) AS count_transplant_surgeries,
        (SELECT COUNT(*) FROM follow_up_reminder f WHERE f.patient_id = p.id) AS count_followups,
        (SELECT COUNT(*) FROM prescription pr WHERE pr.patient_id = p.id) AS count_prescriptions,
        (SELECT MAX(a.start_time) FROM appointment a WHERE a.patient_id = p.id) AS last_appointment
    FROM patient p
    LEFT JOIN patient_doctor pd ON pd.patient_id = p.id
    LEFT JOIN "user" u ON u.id = pd.doctor_id
    WHERE p.status_cadastral = 'ativo'
    ORDER BY p.id, pd.patient_code
    """
    rows = db.session.execute(db.text(sql)).fetchall()

    # ── 2. Estruturar por paciente (um paciente pode ter múltiplos vínculos) ──
    patients_map = {}
    for row in rows:
        pid = row.id
        if pid not in patients_map:
            patients_map[pid] = {
                'id': pid,
                'name': row.name,
                'normalized_name': normalize_patient_name(row.name),
                'phone': row.phone,
                'cpf': row.cpf,
                'city': row.city,
                'created_at': row.created_at.isoformat() if row.created_at else None,
                'last_appointment': row.last_appointment.isoformat() if row.last_appointment else None,
                'count_appointments': row.count_appointments,
                'count_notes': row.count_notes,
                'count_evolutions': row.count_evolutions,
                'count_surgeries': row.count_surgeries,
                'count_transplant_surgeries': row.count_transplant_surgeries,
                'count_followups': row.count_followups,
                'count_prescriptions': row.count_prescriptions,
                'links': [],
                'has_code': False,
            }
        if row.pd_id is not None:
            patients_map[pid]['links'].append({
                'dp_id': row.pd_id,
                'doctor_id': row.doctor_id,
                'doctor_name': row.doctor_name,
                'patient_code': row.patient_code,
            })
            patients_map[pid]['has_code'] = True

    patients_list = list(patients_map.values())

    # ── 3. Índices para rápida busca ──
    by_normalized = defaultdict(list)
    by_phone = defaultdict(list)
    by_cpf = defaultdict(list)
    by_code = defaultdict(list)
    by_first_token = defaultdict(list)
    for p in patients_list:
        nn = p['normalized_name']
        if nn:
            by_normalized[nn].append(p)
            token = nn.split(' ')[0]
            if token:
                by_first_token[token].append(p)
        ph = (p['phone'] or '').strip()
        if ph:
            by_phone[ph].append(p)
        cp = (p['cpf'] or '').strip()
        if cp:
            by_cpf[cp].append(p)
        seen_code_keys = set()
        for link in p['links']:
            key = (link['doctor_id'], link['patient_code'])
            if key not in seen_code_keys:
                seen_code_keys.add(key)
                by_code[key].append(p)

    # ── 4. Detectar problemas ──
    # Cada paciente pode ter múltiplos alertas (lista por id).
    # Isso garante que um paciente seja reportado em todas as categorias relevantes.
    alerts = defaultdict(list)
    alert_keys = set()
    def _add_alert(p, cat, risk, reason, related_ids=None):
        key = (p['id'], cat, reason)
        if key in alert_keys:
            return
        alert_keys.add(key)
        alerts[p['id']].append({
            'id': p['id'],
            'name': p['name'],
            'normalized_name': p['normalized_name'],
            'patient_code': p['links'][0]['patient_code'] if p['links'] else None,
            'doctor_name': p['links'][0]['doctor_name'] if p['links'] else None,
            'phone': p['phone'],
            'cpf': p['cpf'],
            'city': p['city'],
            'created_at': p['created_at'],
            'last_appointment': p['last_appointment'],
            'count_appointments': p['count_appointments'],
            'count_notes': p['count_notes'],
            'count_evolutions': p['count_evolutions'],
            'count_surgeries': p['count_surgeries'],
            'count_transplant_surgeries': p['count_transplant_surgeries'],
            'count_followups': p['count_followups'],
            'count_prescriptions': p['count_prescriptions'],
            'links': p['links'],
            'category': cat,
            'risk': risk,
            'reason': reason,
            'related_ids': related_ids or [],
        })

    # 4a. Códigos duplicados
    for (doctor_id, code), group in by_code.items():
        if len(group) > 1:
            ids = [p['id'] for p in group]
            for p in group:
                _add_alert(p, 'mesmo_código', 'alto', f'Código {code} duplicado com médico {doctor_id}', ids)

    # 4b. Nomes idênticos
    for nn, group in by_normalized.items():
        if len(group) > 1:
            # Skip if the same patient is linked to multiple doctors (different doctor_ids)
            # This is a normal case: one patient with multiple doctors, not a duplicate.
            all_doctor_ids = set()
            for p in group:
                for link in p['links']:
                    all_doctor_ids.add(link['doctor_id'])
            # If there are multiple doctors AND the patient has multiple doctor links,
            # it might be the same patient across doctors. Only flag if the same doctor
            # has the same patient multiple times.
            # Simpler: skip if there are 2+ doctors and all patients in group have unique ids
            # Actually, skip when ALL patients in the group have different doctor_ids
            # (meaning no two patients share the same doctor)
            doctor_ids_per_patient = []
            for p in group:
                d_ids = [link['doctor_id'] for link in p['links']]
                doctor_ids_per_patient.append(d_ids)
            # Check if any two patients share at least one doctor
            shares_doctor = False
            for i in range(len(doctor_ids_per_patient)):
                for j in range(i+1, len(doctor_ids_per_patient)):
                    if set(doctor_ids_per_patient[i]) & set(doctor_ids_per_patient[j]):
                        shares_doctor = True
                        break
                if shares_doctor:
                    break
            if not shares_doctor:
                continue
            ids = [p['id'] for p in group]
            for p in group:
                _add_alert(p, 'provável_duplicado', 'alto', 'Nomes idênticos', ids)

    # 4c. Nomes parecidos (candidate blocking com first-token)
    checked_pairs = set()
    for token, candidates in by_first_token.items():
        for i, p in enumerate(candidates):
            for j in range(i + 1, len(candidates)):
                q = candidates[j]
                key = (min(p['id'], q['id']), max(p['id'], q['id']))
                if key in checked_pairs:
                    continue
                checked_pairs.add(key)
                if not p['normalized_name'] or not q['normalized_name']:
                    continue
                ratio = SequenceMatcher(None, p['normalized_name'], q['normalized_name']).ratio()
                if ratio >= 0.85 and p['normalized_name'] != q['normalized_name']:
                    ids = [p['id'], q['id']]
                    _add_alert(p, 'possível_duplicado', 'médio', f'Nome parecido (sim={round(ratio,2)})', ids)
                    _add_alert(q, 'possível_duplicado', 'médio', f'Nome parecido (sim={round(ratio,2)})', ids)

    # 4d. Mesmo telefone
    for ph, group in by_phone.items():
        if len(group) > 1:
            ids = [p['id'] for p in group]
            for p in group:
                _add_alert(p, 'mesmo_telefone', 'médio', f'Telefone {ph} compartilhado', ids)

    # 4e. Mesmo CPF
    for cp, group in by_cpf.items():
        if len(group) > 1:
            ids = [p['id'] for p in group]
            for p in group:
                _add_alert(p, 'mesmo_cpf', 'alto', f'CPF {cp} compartilhado', ids)

    # 4f. Sem código
    for p in patients_list:
        if not p['has_code']:
            _add_alert(p, 'sem_código', 'baixo', 'Paciente sem código de vínculo médico', [])

    # 4g. Códigos fora da sequência (gap > 1)
    doctor_codes = defaultdict(list)
    for p in patients_list:
        seen = set()
        for link in p['links']:
            key = (link['doctor_id'], link['patient_code'])
            if key not in seen:
                seen.add(key)
                doctor_codes[link['doctor_id']].append((link['patient_code'], p['id']))
    for doctor_id, codes in doctor_codes.items():
        codes.sort(key=lambda x: x[0])
        for i in range(len(codes) - 1):
            gap = codes[i + 1][0] - codes[i][0]
            if gap > 1:
                pid = codes[i + 1][1]
                p = patients_map.get(pid)
                if p:
                    _add_alert(p, 'revisar_manualmente', 'baixo', f'Gap de {gap} códigos após {codes[i][0]} (médico {doctor_id})', [])

    # ── 5. Flatten: um paciente pode aparecer múltiplas vezes (cada alerta) ──
    # Ordenar por gravidade
    categories = []
    for pid, alert_list in alerts.items():
        categories.extend(alert_list)

    risk_order = {'alto': 0, 'médio': 1, 'baixo': 2}
    categories.sort(key=lambda r: (risk_order.get(r['risk'], 3), r['name'] or ''))

    return jsonify({
        'success': True,
        'count': len(categories),
        'records': categories,
    })


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
        data = request.form.to_dict() if request.form else {}
    if not data and request.content_length and request.content_length > 0:
        app.logger.warning(
            "EMPTY BODY finalizar_atendimento: content_type=%s len=%s raw=%s",
            request.content_type, request.content_length,
            request.get_data(as_text=True)[:200]
        )
        return jsonify({'success': False, 'error': 'Body recebido vazio ou não-JSON'}), 400
    
    # consultation_started não é mais obrigatório (permite salvar consultas retroativas)
    
    try:
        category = data.get('category', 'patologia')
        duration = data.get('duration')
        appointment_id = data.get('appointment_id')  # Chave de agrupamento
        finalized_at = get_brazil_time()
        consultation_started_at = parse_datetime_with_tz(data['consultation_started_at']) if data.get('consultation_started_at') else None
        
        # Fetch patient object early for reuse
        patient = db.session.get(Patient, patient_id)
        
        # Salvar cada seção como nota separada
        sections = ['queixa', 'anamnese', 'diagnostico']
        note_ids = {}

        # ATENÇÃO: Garantir status "atendido" e saída da sala de espera
        # Fazemos isso no início da transação para garantir que ocorra mesmo se houver erro posterior
        if appointment_id:
            try:
                # Buscar o agendamento sem restrição de médico para correção de bugs antigos
                appt_to_update = db.session.get(Appointment, int(appointment_id))
                if appt_to_update and appt_to_update.patient_id == patient_id:
                    appt_to_update.status = 'atendido'
                    appt_to_update.waiting = False
                    appt_to_update.is_finalized = True
                    appt_to_update.finalized_at = finalized_at
                    if consultation_started_at:
                        appt_to_update.consultation_started_at = consultation_started_at
                    if not appt_to_update.checked_in_time:
                        appt_to_update.checked_in_time = get_brazil_time()
                    db.session.add(appt_to_update)
                    db.session.flush() # Força a ida para o DB dentro da transação
                    app.logger.debug(f"Appointment {appointment_id} forçado para atendido")
                else:
                    app.logger.debug(f"Appointment {appointment_id} não encontrado ou paciente não confere. Anulando ID para evitar erro de FK.")
                    appointment_id = None # Anular para evitar erro de FK se o agendamento sumiu
            except Exception as appt_err:
                print(f"Erro ao atualizar status do agendamento inicial: {appt_err}")
                appointment_id = None

        
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
                transplant_indication=transplant_indication,
                finalized_at=finalized_at,
                is_finalized=True
            )
            db.session.add(conduta_note)
            db.session.flush()
            note_ids['conduta'] = conduta_note.id
        elif note_ids:
            fallback_note = db.session.get(Note, next(reversed(note_ids.values())))
            if fallback_note:
                fallback_note.is_finalized = True
                fallback_note.finalized_at = finalized_at
                if fallback_note.consultation_duration is None:
                    fallback_note.consultation_duration = duration
                db.session.add(fallback_note)
        
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
            
            cosmetic_procedures_data = data.get('cosmetic_procedures', [])
            conduta_note_id = note_ids.get('conduta')
            
            if conduta_note_id and cosmetic_procedures_data:
                # Batch update de lembretes ANTES do loop
                performed_proc_names = [p['name'] for p in cosmetic_procedures_data if p.get('performed', False)]
                non_performed_proc_names = [p['name'] for p in cosmetic_procedures_data if not p.get('performed', False)]
                
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
                for proc_item in cosmetic_procedures_data:
                    proc_name = proc_item['name']
                    
                    # Criar novo plano para este atendimento
                    from datetime import datetime as dt
                    
                    # Processar data de realização se fornecida
                    performed_date_value = None
                    if proc_item.get('performedDate'):
                        try:
                            performed_date_value = dt.strptime(proc_item.get('performedDate', ''), '%Y-%m-%d').date()
                        except (ValueError, TypeError, AttributeError):
                            performed_date_value = None
                    
                    plan_name = (proc_item.get('name') or '').strip()
                    if not plan_name:
                        raise ValueError('name é obrigatório em cosmetic_procedures')

                    plan_obj = CosmeticProcedurePlan(
                        note_id=conduta_note_id,
                        name=plan_name,
                        procedure_name=proc_item.get('procedure_name', proc_name),
                        planned_value=float(proc_item['value']),
                        final_budget=float(proc_item.get('budget', proc_item['value'])),
                        follow_up_months=int(proc_item['months']),
                        observations=proc_item.get('observations', '')
                    )
                    db.session.add(plan_obj)
                    db.session.flush()

                    if bool(proc_item.get('performed', False)) and performed_date_value:
                        execution_obj = ProcedureExecution(
                            plan_id=plan_obj.id,
                            performed_date=datetime.combine(performed_date_value, datetime.min.time()),
                            execution_status='realizada',
                            was_performed=True,
                            charged_value=float(proc_item.get('budget', proc_item['value'])),
                            notes=proc_item.get('observations', ''),
                            followup_status='pendente',
                            created_by=current_user.id,
                            updated_by=current_user.id,
                        )
                        db.session.add(execution_obj)

                        # Auto-sync aba Botox no Google Sheets
                        _proc_type = (plan_obj.procedure_name or proc_name or '').lower()
                        if 'botox' in _proc_type:
                            try:
                                from services.google_sheets import append_botox_row
                                from dateutil.relativedelta import relativedelta as _rdelta
                                _fu_date = (performed_date_value + _rdelta(months=5)).strftime('%d/%m/%Y')
                                append_botox_row({
                                    'patient_name':  patient.name if patient else f'Paciente #{patient_id}',
                                    'phone':         patient.phone if patient else '',
                                    'performed_date': performed_date_value.strftime('%d/%m/%Y'),
                                    'followup_date':  _fu_date,
                                })
                            except Exception as _be:
                                print(f'Erro ao registrar Botox (não-crítico): {_be}')

                    # Criar novo lembrete APENAS para não realizados
                    if not proc_item.get('performed', False):
                        follow_up_date = (get_brazil_time() + timedelta(days=30 * int(proc_item['months']))).date()
                        reminder_obj = FollowUpReminder(
                            patient_id=patient_id,
                            procedure_name=proc_name,
                            scheduled_date=follow_up_date,
                            reminder_type='cosmetic_follow_up'
                        )
                        db.session.add(reminder_obj)
            
        # CRIAR CHECKOUT AUTOMATICAMENTE para procedimentos realizados
        checkout_amount = data.get('checkout_amount', 0)
        checkout_procedures = data.get('checkout_procedures', [])
        consultation_type = data.get('consultation_type', 'Particular')
        
        if checkout_procedures:
            try:
                # Adicionar valor da consulta conforme tipo
                procedures_list = []
                for proc in checkout_procedures:
                    try:
                        val = float(proc.get('budget', proc.get('value', 0)))
                    except (ValueError, TypeError):
                        val = 0.0
                    procedures_list.append({
                        'name': proc.get('name', 'Procedimento'),
                        'value': val
                    })
                
                # Adicionar taxa de consulta conforme tipo de consulta
                total_amount = 0.0
                try:
                    total_amount = float(checkout_amount)
                except (ValueError, TypeError):
                    total_amount = 0.0
                
                # Use a default empty dict if CONSULTATION_PRICES is not defined or other issue
                try:
                    consultation_fee = CONSULTATION_PRICES.get(consultation_type, 0.0)
                except (AttributeError, TypeError):
                    consultation_fee = 0.0

                if consultation_fee > 0:
                    procedures_list.insert(0, {
                        'name': f'Consulta {consultation_type}',
                        'value': consultation_fee
                    })
                    total_amount += consultation_fee
                
                from models import Payment
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
                print(f"✓✓✓ PAYMENT CRIADO: R${total_amount} - {consultation_type} - Paciente {patient_id}")
            except Exception as pay_err:
                print(f"Erro ao criar pagamento: {pay_err}")
                # Não interrompe o fluxo principal se o pagamento falhar
        
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
                    case_type=surgical_planning.get('case_type', 'primaria'),
                    body_hair_needed=surgical_planning.get('body_hair_needed', False),
                    eyebrow_transplant=surgical_planning.get('eyebrow_transplant', False),
                    beard_transplant=surgical_planning.get('beard_transplant', False),
                    feminine_hair_transplant=surgical_planning.get('feminine_hair_transplant', False),
                    frontal_transplant=surgical_planning.get('frontal', False),
                    crown_transplant=surgical_planning.get('crown', False),
                    complete_transplant=surgical_planning.get('complete', False),
                    complete_with_body_hair=surgical_planning.get('complete_body_hair', False),
                    dense_packing=surgical_planning.get('dense_packing', False),
                    surgical_planning=surgical_planning.get('surgical_planning_text', ''),
                    clinical_conduct=surgical_planning.get('clinical_conduct', '')
                )
                db.session.add(transplant)
                
                # Marcar indicação no paciente se houver classificação Norwood
                if surgical_planning.get('norwood') and patient:
                    patient.has_transplant_indication = True
                    db.session.add(patient)

        if patient and data.get('transplant_indication') in ('sim', 'nao'):
            patient.has_transplant_indication = (data.get('transplant_indication') == 'sim')
            db.session.add(patient)
        
        # Atualizar status do agendamento para "atendido"
        app.logger.debug(f"finalizar: appointment_id={appointment_id}, patient_id={patient_id}, doctor_id={current_user.id}")
        
        if appointment_id:
            # Primeiro buscar sem filtro de doctor para debug
            appointment_check_val = Appointment.query.filter_by(id=appointment_id).first()
            if appointment_check_val:
                app.logger.debug(f"Appointment encontrado - doctor_id no DB: {appointment_check_val.doctor_id}, current_user.id: {current_user.id}")
            
            # Buscar o appointment (sem filtro de doctor_id para permitir atualizar)
            appointment_final = Appointment.query.filter_by(
                id=appointment_id,
                patient_id=patient_id
            ).first()
            
            if appointment_final:
                appointment_final.status = 'atendido'
                appointment_final.waiting = False
                appointment_final.is_finalized = True
                appointment_final.finalized_at = finalized_at
                if consultation_started_at and not appointment_final.consultation_started_at:
                    appointment_final.consultation_started_at = consultation_started_at
                if not appointment_final.checked_in_time:
                    appointment_final.checked_in_time = get_brazil_time()
                db.session.add(appointment_final)
                app.logger.debug(f"Appointment {appointment_id} updated to atendido, status={appointment_final.status}")
            else:
                print(f"Warning: Appointment {appointment_id} not found for patient {patient_id}")
        
        # Commit da transação
        db.session.commit()
        
        # === GOOGLE SHEETS: Registrar procedimentos realizados ===
        try:
            from services.google_sheets import append_procedures_batch
            from dateutil.relativedelta import relativedelta
            
            patient_name = patient.name if patient else f"Paciente #{patient_id}"
            patient_phone = patient.phone if patient else ''
            now = get_brazil_time()

            gs_rows = []
            if category == 'cosmiatria':
                for proc in data.get('cosmetic_procedures', []):
                    if proc.get('performed', False):
                        performed_date = now.date()
                        # Use get to handle potential missing keys or non-integer values
                        try:
                            # Tentar pegar de 'months' ou 'follow_up_months'
                            m_val = proc.get('months') or proc.get('follow_up_months') or 0
                            follow_up_months = int(m_val)
                        except (ValueError, TypeError):
                            follow_up_months = 0
                            
                        return_date_str = ''
                        if follow_up_months > 0:
                            try:
                                return_date = performed_date + relativedelta(months=follow_up_months)
                                return_date_str = return_date.strftime('%d/%m/%Y')
                            except:
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
                    app.logger.debug(f"{len(gs_rows)} procedimentos enviados para Google Sheets")

                # Aba Botox: envia cada Botox realizado também para a aba dedicada
                try:
                    from services.google_sheets import append_botox_row
                    from dateutil.relativedelta import relativedelta as _rdelta
                    for _row in gs_rows:
                        if 'botox' in _row.get('procedure_name', '').lower():
                            _pd = datetime.strptime(_row['procedure_date'], '%d/%m/%Y').date()
                            _fu = (_pd + _rdelta(months=5)).strftime('%d/%m/%Y')
                            append_botox_row({
                                'patient_name':  _row['patient_name'],
                                'phone':         _row['phone'],
                                'performed_date': _row['procedure_date'],
                                'followup_date':  _fu,
                            })
                except Exception as _be:
                    print(f"Erro ao registrar Botox na aba Botox (não-crítico): {_be}")
            
            elif category == 'transplante_capilar':
                from services.google_sheets import append_transplant_data
                append_transplant_data([{
                    'patient_name': patient_name,
                    'phone': patient_phone or '',
                    'consult_date': now.strftime('%d/%m/%Y'),
                    'status': 'pendente',
                    'surgery_date': ''
                }])
        except Exception as gs_err:
            print(f"Erro ao integrar com Google Sheets (não-crítico): {gs_err}")

        # === RESPOSTA FINAL ===
        return jsonify({'success': True})

    except Exception as e:
        import traceback
        print(f"ERRO CRÍTICO EM finalizar_atendimento (Patient: {patient_id}): {str(e)}")
        print(traceback.format_exc())
        try:
            db.session.rollback()
        except:
            pass
        return jsonify({'success': False, 'error': f'Erro interno: {str(e)}'}), 500

@app.route('/api/prontuario/<int:patient_id>/cosmetic-plan', methods=['POST'])
@login_required
def save_cosmetic_plan(patient_id):
    if not current_user.is_doctor():
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403

    data = request.get_json(silent=True) or {}

    try:
        from models import CosmeticProcedurePlan, Note

        plan_name = (data.get('name') or '').strip()
        procedure_name = (data.get('procedure_name') or data.get('name') or '').strip()
        planned_value = float(data.get('value', 0) or 0)
        final_budget = float(data.get('budget', planned_value) or planned_value)
        follow_up_months = int(data.get('months', 6) or 6)
        observations = data.get('observations', '')

        if not plan_name:
            return jsonify({'success': False, 'error': 'Nome do plano é obrigatório'}), 400
        if not procedure_name:
            return jsonify({'success': False, 'error': 'Procedimento é obrigatório'}), 400
        if planned_value <= 0:
            return jsonify({'success': False, 'error': 'Valor deve ser maior que zero'}), 400

        consultation_key = str(data.get('consultation_key') or '').strip()
        fallback_consultation_key = str(data.get('fallback_consultation_key') or '').strip()

        target_note = None
        appointment_id = None

        if consultation_key.startswith('note_'):
            try:
                note_id = int(consultation_key.replace('note_', ''))
                note_candidate = db.session.get(Note, note_id)
                if (
                    note_candidate
                    and note_candidate.patient_id == patient_id
                    and note_candidate.note_type == 'conduta'
                ):
                    target_note = note_candidate
            except (ValueError, TypeError):
                target_note = None
        elif consultation_key.isdigit():
            appointment_id = int(consultation_key)

        if target_note is None and fallback_consultation_key.startswith('note_'):
            try:
                note_id = int(fallback_consultation_key.replace('note_', ''))
                note_candidate = db.session.get(Note, note_id)
                if (
                    note_candidate
                    and note_candidate.patient_id == patient_id
                    and note_candidate.note_type == 'conduta'
                ):
                    target_note = note_candidate
            except (ValueError, TypeError):
                target_note = None

        if target_note is None and appointment_id:
            target_note = Note.query.filter_by(
                patient_id=patient_id,
                appointment_id=appointment_id,
                note_type='conduta'
            ).order_by(Note.id.desc()).first()

        if target_note is None and appointment_id:
            # busca sem filtro de categoria
            target_note = Note.query.filter_by(
                patient_id=patient_id,
                appointment_id=appointment_id,
                note_type='conduta'
            ).order_by(Note.id.desc()).first()

        if target_note is None:
            # busca a conduta mais recente do paciente com categoria cosmiatria
            target_note = Note.query.filter_by(
                patient_id=patient_id,
                note_type='conduta',
                category='cosmiatria'
            ).order_by(Note.id.desc()).first()

        if target_note is None:
            # última tentativa: qualquer conduta recente do paciente
            target_note = Note.query.filter_by(
                patient_id=patient_id,
                note_type='conduta'
            ).order_by(Note.id.desc()).first()

        if target_note is None:
            target_note = Note(
                patient_id=patient_id,
                doctor_id=current_user.id,
                appointment_id=appointment_id,
                note_type='conduta',
                category='cosmiatria',
                content='',
                finalized_at=get_brazil_time(),
                is_finalized=True
            )
            db.session.add(target_note)
            db.session.flush()

        plan = CosmeticProcedurePlan(
            note_id=target_note.id,
            name=plan_name,
            procedure_name=procedure_name,
            planned_value=planned_value,
            final_budget=final_budget,
            follow_up_months=follow_up_months,
            observations=observations
        )
        db.session.add(plan)
        db.session.commit()

        return jsonify({
            'success': True,
            'plan': {
                'id': plan.id,
                'name': plan.name,
                'procedure_name': plan.procedure_name,
                'planned_value': float(plan.planned_value) if plan.planned_value else 0,
                'final_budget': float(plan.final_budget) if plan.final_budget else 0,
                'follow_up_months': plan.follow_up_months,
                'observations': plan.observations,
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': f'Erro ao salvar planejamento: {str(e)}'}), 500

@app.route('/api/prontuario/<int:patient_id>/generate-budget', methods=['POST'])
@login_required
def generate_budget_pdf(patient_id):
    """Gera orçamento PDF de procedimentos cosméticos"""
    role = (getattr(current_user, 'role', '') or '').lower()
    role_clinico = (getattr(current_user, 'role_clinico', '') or '').upper()
    if role not in {'secretaria', 'medico'} and role_clinico not in {'SECRETARY', 'ADMIN'}:
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
    
    if 'tags' in data:
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
            db.and_(ChatMessage.sender_id == current_user.id, ChatMessage.recipient_id == with_user_id),
            db.and_(ChatMessage.sender_id == with_user_id, ChatMessage.recipient_id == current_user.id)
        )
    ).order_by(ChatMessage.id.asc()).all()
    
    try:
        return jsonify([{
            'id': msg.id,
            'senderId': msg.sender_id,
            'recipientId': msg.recipient_id,
            'message': msg.message,
            'timestamp': format_brazil_datetime(msg.created_at).split(' ')[1] if msg.created_at else '',
            'read': msg.read if hasattr(msg, 'read') else False
        } for msg in messages])
    except Exception as e:
        print(f'[CHAT ERROR] Serialization failed: {e}')
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/chat/send', methods=['POST'])
@login_required
def send_message():
    data = request.get_json(silent=True) or request.form
    if not hasattr(data, 'get'):
        return jsonify({'error': 'Dados inválidos'}), 400
    recipient_id = data.get('recipient_id')
    if not recipient_id:
        return jsonify({'error': 'recipient_id é obrigatório'}), 400

    try:
        recipient_id = int(recipient_id)
    except (TypeError, ValueError):
        return jsonify({'error': 'Destinatário inválido'}), 400

    if recipient_id == current_user.id:
        return jsonify({'error': 'Não é possível enviar mensagem para si mesmo'}), 400
    
    recipient = db.session.get(User, recipient_id)
    if not recipient:
        return jsonify({'error': 'Destinatário não encontrado'}), 404
    
    message_text = str(data.get('message') or '').strip()
    if not message_text:
        return jsonify({'error': 'Mensagem vazia'}), 400
    if len(message_text) > 4000:
        return jsonify({'error': 'Mensagem excede o limite de 4000 caracteres'}), 400

    message_obj = ChatMessage(
        sender_id=current_user.id,
        recipient_id=recipient_id,
        message=message_text,
        created_at=get_brazil_time().replace(tzinfo=None)
    )
    db.session.add(message_obj)
    db.session.commit()
    return jsonify({'success': True, 'id': message_obj.id})

@app.route('/api/chat/mark_read', methods=['POST'])
@login_required
def mark_messages_read():
      data = request.get_json(silent=True) or request.form
      if not hasattr(data, 'get'):
          return jsonify({'success': False, 'error': 'Dados inválidos'}), 400
      from_user_id = data.get('from_user_id')
      if from_user_id:
          try:
              from_user_id = int(from_user_id)
          except (TypeError, ValueError):
              return jsonify({'success': False, 'error': 'Remetente inválido'}), 400
      
      query = db.session.query(ChatMessage.id).filter(ChatMessage.recipient_id == current_user.id)
      if from_user_id:
          query = query.filter(ChatMessage.sender_id == from_user_id)
      
      unread_message_ids = query.outerjoin(
          MessageRead,
          db.and_(MessageRead.message_id == ChatMessage.id, MessageRead.user_id == current_user.id)
      ).filter(MessageRead.id.is_(None)).all()
      
      if not unread_message_ids:
          return jsonify({'success': True, 'count': 0})
      
      read_records = [MessageRead(message_id=msg_id[0], user_id=current_user.id) for msg_id in unread_message_ids]
      try:
          db.session.bulk_save_objects(read_records)
          db.session.commit()
          return jsonify({'success': True, 'count': len(read_records)})
      except Exception as e:
          db.session.rollback()
          return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/chat/latest_unread')
@login_required
def get_latest_unread():
      def _chat_display_name(user):
          if not user:
              return "Sistema"

          raw_name = (user.name or '').strip()
          username = (user.username or '').strip().lower()

          # Compatibilidade com base legada: usuário técnico/admin que representa o Dr. Arthur
          if username == 'admin' and (not raw_name or raw_name.lower() == 'admin'):
              return 'Dr. Arthur'

          return raw_name or user.email or user.username or "Sistema"

      subquery = db.session.query(MessageRead.message_id).filter(MessageRead.user_id == current_user.id)
      latest = ChatMessage.query.filter(
          ChatMessage.recipient_id == current_user.id,
          ~ChatMessage.id.in_(subquery)
      ).order_by(ChatMessage.created_at.desc()).first()
      
      if latest:
          return jsonify({
              'id': latest.id,
              'from_user_id': latest.sender_id,
              'from_name': _chat_display_name(latest.sender),
              'message': (latest.message[:80] + ('...' if len(latest.message) > 80 else '')) if latest.message else "",
              'created_at': latest.created_at.isoformat()
          })
      return jsonify({'id': None})

@app.route('/api/chat/unread_count')
@login_required
def get_unread_count():
      from_user_id = request.args.get('from_user_id', type=int)
      query = db.session.query(ChatMessage).filter(ChatMessage.recipient_id == current_user.id)
      if from_user_id:
          query = query.filter(ChatMessage.sender_id == from_user_id)
      
      count = query.outerjoin(
          MessageRead,
          db.and_(MessageRead.message_id == ChatMessage.id, MessageRead.user_id == current_user.id)
      ).filter(MessageRead.id.is_(None)).count()
      return jsonify({'count': count})

@app.route('/api/chat/contacts')
@login_required
def get_chat_contacts():
      def _chat_role_kind(user):
          role = (user.role or '').strip().lower()
          role_clinico = (user.role_clinico or '').strip().upper()

          if role == 'medico' or role_clinico in ('DERM', 'CP'):
              return 'medico'
          if role == 'secretaria' or role_clinico == 'SECRETARY':
              return 'secretaria'
          return None

      def _chat_display_name(user):
          raw_name = (user.name or '').strip()
          username = (user.username or '').strip().lower()

          # Compatibilidade com base legada: usuário técnico/admin que representa o Dr. Arthur
          if username == 'admin' and (not raw_name or raw_name.lower() == 'admin'):
              return 'Dr. Arthur'

          return raw_name or user.email or user.username or 'Usuário'

      users = User.query.filter(User.id != current_user.id).all()
      contacts = []
      for user in users:
          role_kind = _chat_role_kind(user)
          if role_kind is None:
              # Excluir perfis administrativos/técnicos do chat clínico
              continue

          unread_count = db.session.query(ChatMessage).filter(
              ChatMessage.recipient_id == current_user.id,
              ChatMessage.sender_id == user.id
          ).outerjoin(
              MessageRead,
              db.and_(MessageRead.message_id == ChatMessage.id, MessageRead.user_id == current_user.id)
          ).filter(MessageRead.id.is_(None)).count()
          
          contacts.append({
              'id': user.id,
              'name': _chat_display_name(user),
              'role': role_kind,
              'unread_count': unread_count
          })

      contacts.sort(key=lambda c: (0 if c['role'] == 'medico' else 1, c['name'].lower()))
      return jsonify(contacts)
  

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
        executions = ProcedureExecution.query.filter_by(plan_id=plan.id).order_by(
            ProcedureExecution.performed_date.desc().nullslast(),
            ProcedureExecution.created_at.desc()
        ).all()

        plans_data.append({
            'id': plan.id,
            'name': plan.name,
            'procedure_name': plan.procedure_name,
            'status': plan.status,
            'planned_value': plan.planned_value,
            'final_budget': plan.final_budget,
            'follow_up_months': plan.follow_up_months,
            'observations': plan.observations,
            'created_at': note.created_at.isoformat() if note else None,
            'executions': [_serialize_execution(execution) for execution in executions]
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
        
        executions = ProcedureExecution.query.filter_by(plan_id=plan.id).order_by(
            ProcedureExecution.performed_date.desc().nullslast(),
            ProcedureExecution.created_at.desc()
        ).all()

        grouped_plans[consultation_key].append({
            'id': plan.id,
            'name': plan.name,
            'procedure_name': plan.procedure_name,
            'status': plan.status,
            'planned_value': float(plan.planned_value) if plan.planned_value else 0,
            'final_budget': float(plan.final_budget) if plan.final_budget else 0,
            'follow_up_months': plan.follow_up_months,
            'observations': plan.observations,
            'created_at': plan.created_at.isoformat() if plan.created_at else None,
            'executions': [_serialize_execution(execution) for execution in executions]
        })
    
    result = []
    for consultation_key, procedures in grouped_plans.items():
        result.append({
            'consultation_key': consultation_key,
            'consultation_info': consultation_info[consultation_key],
            'procedures': procedures
        })
    
    result.sort(key=lambda x: x['consultation_info']['date'], reverse=True)

    pending_by_date = {}
    realized_by_date = {}
    for item in result:
        for procedure in item.get('procedures', []):
            executions = procedure.get('executions') or []
            if not executions:
                key = (procedure.get('created_at') or item['consultation_info']['date'] or '')[:10]
                pending_by_date.setdefault(key, []).append(procedure)
                continue
            for execution in executions:
                status = execution.get('execution_status') or ('realizada' if execution.get('was_performed') else 'agendada')
                base_date = execution.get('performed_date') if status == 'realizada' else execution.get('scheduled_date')
                key = (base_date or procedure.get('created_at') or item['consultation_info']['date'] or '')[:10]
                target = realized_by_date if status == 'realizada' else pending_by_date
                target.setdefault(key, []).append({
                    'plan_id': procedure.get('id'),
                    'procedure_name': procedure.get('procedure_name'),
                    'status': status,
                    'execution': execution,
                    'color': '#198754' if status == 'realizada' else '#ffc107'
                })

    return jsonify({'success': True, 'grouped_plans': result, 'pending_by_date': pending_by_date, 'realized_by_date': realized_by_date})


@app.route('/api/prontuario/cosmetic-plan/<int:plan_id>', methods=['DELETE'])
@login_required
def delete_cosmetic_plan(plan_id):
    if not current_user.is_doctor() and not current_user.is_secretary():
        return jsonify({'success': False, 'error': 'Não autorizado'}), 403

    plan = CosmeticProcedurePlan.query.get_or_404(plan_id)
    db.session.delete(plan)
    db.session.commit()
    return jsonify({'success': True})


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
    if 'follow_up_months' in data:
        plan.follow_up_months = int(data['follow_up_months'])
    if 'name' in data:
        name = (data.get('name') or '').strip()
        if not name:
            return jsonify({'success': False, 'error': 'name é obrigatório'}), 400
        plan.name = name
    if 'status' in data:
        status = (data.get('status') or '').strip().lower()
        if status not in {'ativo', 'pausado', 'concluido', 'cancelado'}:
            return jsonify({'success': False, 'error': 'status inválido'}), 400
        plan.status = status
    
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
    
    app.logger.debug(f"Found {len(payments)} payments for today")
    
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
    
    app.logger.debug(f"toggle: Payment {payment_id} - new_total={new_total}, procedures={procedures}")
    
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

@app.route('/api/evolution/<int:evo_id>', methods=['DELETE'])
@login_required
def delete_evolution(evo_id):
    """Deletar evolução"""
    evo = Evolution.query.get_or_404(evo_id)
    if not can_manage_owned_record(current_user, evo.doctor_id):
        return jsonify({'success': False, 'error': 'Não autorizado'}), 403
    
    db.session.delete(evo)
    db.session.commit()
    return jsonify({'success': True})

@app.route('/api/patient/<int:patient_id>/photo', methods=['DELETE'])
@login_required
def delete_patient_photo(patient_id):
    """Remover foto do paciente"""
    patient = Patient.query.get_or_404(patient_id)
    delete_stored_patient_photo(patient)
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

if os.environ.get('DISABLE_SCHEDULER') != '1':
    start_smart_no_show_scheduler(app)

# Note: When using Gunicorn for production, app.run() is not needed
# Gunicorn handles the server execution
@app.route('/api/patients/<int:id>/ivp', methods=['PATCH'])
@login_required
def update_patient_ivp(id):
    if not current_user.is_doctor():
        return jsonify({'success': False, 'error': 'Apenas médicos podem classificar pacientes'}), 403
    
    patient = Patient.query.get_or_404(id)
    data = request.get_json()
    
    if 'ivp_stars' in data:
        stars = data.get('ivp_stars')
        if stars is not None:
            try:
                stars = int(stars)
                if stars < 0 or stars > 3:
                    return jsonify({'success': False, 'error': 'Valor de estrelas inválido (0-3)'}), 400
            except ValueError:
                return jsonify({'success': False, 'error': 'Valor de estrelas inválido'}), 400
        
        patient.ivp_stars = stars
        patient.ivp_manual_override = data.get('ivp_manual_override', False)
        patient.ivp_updated_at = get_brazil_time()
        
        db.session.commit()
        return jsonify({'success': True})
    
    return jsonify({'success': False, 'error': 'Dados incompletos'}), 400

@app.route('/api/admin/recalculate-evolution/<int:appointment_id>', methods=['POST'])
@login_required
def admin_recalculate_evolution(appointment_id):
    if not current_user.is_doctor():
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403
        
    from scripts.generate_missing_evolutions import generate_evolution_for_appointment
    success, message = generate_evolution_for_appointment(appointment_id)
    
    if success:
        return jsonify({'success': True, 'message': message})
    else:
        return jsonify({'success': False, 'error': message})

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

@app.context_processor
def inject_asset_version():
    def asset_version(filename):
        try:
            return int(os.path.getmtime(os.path.join(app.static_folder, filename)))
        except OSError:
            return 1

    return {'asset_version': asset_version}


@app.context_processor
def inject_environment_flags():
    from config import IS_PRODUCTION
    return {
        'IS_PRODUCTION': IS_PRODUCTION,
        'IS_PREVIEW': not IS_PRODUCTION,
    }
