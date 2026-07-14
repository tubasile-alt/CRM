from flask import Blueprint, current_app, jsonify, request
from flask_login import current_user, login_required

from models import CosmeticProcedurePlan, Note, ProcedureExecution, db
from services.clinic_time import get_brazil_time
from services.execution_service import (
    _build_execution_from_payload,
    _parse_date_or_datetime,
    _serialize_execution,
)


cosmetic_api_bp = Blueprint('cosmetic_api', __name__)


@cosmetic_api_bp.route('/api/cosmetic-plans/<int:plan_id>/perform', methods=['POST'])
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


@cosmetic_api_bp.route('/api/cosmetic-plans/<int:plan_id>/executions', methods=['POST'])
@login_required
def create_plan_execution(plan_id):
    app = current_app._get_current_object()
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


@cosmetic_api_bp.route('/api/cosmetic-plans/<int:plan_id>/executions', methods=['GET'])
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


@cosmetic_api_bp.route('/api/executions', methods=['GET'])
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


@cosmetic_api_bp.route('/api/executions/<int:execution_id>', methods=['PUT'])
@login_required
def update_execution(execution_id):
    app = current_app._get_current_object()
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


@cosmetic_api_bp.route('/api/executions/<int:execution_id>', methods=['DELETE'])
@login_required
def delete_execution(execution_id):
    app = current_app._get_current_object()
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


@cosmetic_api_bp.route('/api/prontuario/<int:patient_id>/cosmetic-plans', methods=['GET'])
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


@cosmetic_api_bp.route('/api/prontuario/<int:patient_id>/cosmetic-plans-grouped', methods=['GET'])
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
            _ = appointment
            
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


@cosmetic_api_bp.route('/api/prontuario/cosmetic-plan/<int:plan_id>', methods=['DELETE'])
@login_required
def delete_cosmetic_plan(plan_id):
    if not current_user.is_doctor() and not current_user.is_secretary():
        return jsonify({'success': False, 'error': 'Não autorizado'}), 403

    plan = CosmeticProcedurePlan.query.get_or_404(plan_id)
    db.session.delete(plan)
    db.session.commit()
    return jsonify({'success': True})


@cosmetic_api_bp.route('/api/prontuario/cosmetic-plan/<int:plan_id>', methods=['PATCH'])
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
