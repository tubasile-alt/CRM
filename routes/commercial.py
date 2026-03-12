from datetime import date, datetime
from urllib.parse import quote

from flask import Blueprint, abort, jsonify, render_template, request
from flask_login import current_user, login_required
from sqlalchemy import case

from models import CommercialTask, PlasticSurgeryEncounter, User, db, get_brazil_time
from services.commercial import (
    CP_DOCTOR_USERNAMES,
    DERMA_DASHBOARD_DOCTOR_USERNAMES,
    DERMA_SOURCE_TYPE,
    VALID_PRIORITIES,
    VALID_STATUSES,
    build_whatsapp_message,
    can_access_commercial,
    get_commercial_filter_doctors,
    get_cp_doctors,
    get_derma_dashboard_doctors,
    monday_and_sunday,
)

commercial_bp = Blueprint('commercial', __name__, url_prefix='/commercial')
commercial_api_bp = Blueprint('commercial_api', __name__, url_prefix='/api/commercial')


def _ensure_commercial_access():
    if not can_access_commercial(current_user):
        abort(403)


def _allowed_derma_doctor_ids():
    return [d.id for d in get_derma_dashboard_doctors()]


@commercial_bp.route('')
@login_required
def dashboard_page():
    _ensure_commercial_access()
    doctors = get_commercial_filter_doctors()
    return render_template('commercial_dashboard.html', doctors=doctors)


@commercial_bp.route('/task/<int:task_id>')
@login_required
def task_page(task_id):
    _ensure_commercial_access()
    task = CommercialTask.query.filter_by(id=task_id, source_type=DERMA_SOURCE_TYPE).first_or_404()
    if task.doctor_id not in _allowed_derma_doctor_ids() or not _task_has_cosmiatria_payload(task):
        abort(404)
    return render_template('commercial_task.html', task=task)


def _doctor_filter(query):
    allowed_ids = _allowed_derma_doctor_ids()
    query = query.filter(CommercialTask.doctor_id.in_(allowed_ids))

    doctor_id = request.args.get('doctor_id', type=int)
    if doctor_id and doctor_id in allowed_ids:
        query = query.filter(CommercialTask.doctor_id == doctor_id)
    return query


def _serialize_task(task):
    return {
        'id': task.id,
        'patient_id': task.patient_id,
        'patient_name_snapshot': task.patient_name_snapshot,
        'doctor_id': task.doctor_id,
        'doctor_name_snapshot': task.doctor_name_snapshot,
        'consultation_id': task.consultation_id,
        'consultation_date': task.consultation_date.isoformat() if task.consultation_date else None,
        'source_type': task.source_type,
        'procedures': task.snapshot_items,
        'total_value': task.total_value_float,
        'status': task.status,
        'priority': task.priority,
        'seller_notes': task.seller_notes or '',
        'next_followup_date': task.next_followup_date.isoformat() if task.next_followup_date else None,
        'last_contact_at': task.last_contact_at.isoformat() if task.last_contact_at else None,
        'whatsapp_templates': {
            'pos_consulta': _whatsapp_url(task, 'pos_consulta'),
            'orcamento': _whatsapp_url(task, 'orcamento'),
            'follow_up': _whatsapp_url(task, 'follow_up'),
            'retomada': _whatsapp_url(task, 'retomada'),
        },
    }


def _whatsapp_url(task, template):
    phone = (task.patient.phone if task.patient else '') or ''
    normalized_phone = ''.join(ch for ch in phone if ch.isdigit())
    if normalized_phone.startswith('0'):
        normalized_phone = normalized_phone[1:]
    if normalized_phone and not normalized_phone.startswith('55'):
        normalized_phone = f'55{normalized_phone}'

    message = build_whatsapp_message(task, template=template)
    base = f'https://wa.me/{normalized_phone}' if normalized_phone else 'https://wa.me/'
    return f'{base}?text={quote(message)}'


def _task_has_cosmiatria_payload(task):
    # Aceitar tarefas importadas (sem procedures específicas) e tarefas com procedures
    items = task.snapshot_items or []
    if not items:
        # Tarefas importadas sem procedures ainda contam como válidas
        return True
    for item in items:
        name = (item.get('name') or '').strip()
        planned = float(item.get('planned_value') or 0)
        budget = float(item.get('budget_value') or 0)
        if name or planned > 0 or budget > 0 or bool(item.get('performed')):
            return True
    return False


def _base_derma_query():
    return CommercialTask.query.filter(CommercialTask.source_type == DERMA_SOURCE_TYPE)


def _priority_ordering():
    return case(
        (CommercialTask.priority == 'alta', 0),
        (CommercialTask.priority == 'media', 1),
        (CommercialTask.priority == 'baixa', 2),
        else_=3,
    )


def _list_today_tasks():
    today = date.today()
    query = _base_derma_query().filter(
        CommercialTask.consultation_date == today,
        CommercialTask.status != 'fechado',
        CommercialTask.status != 'perdido',
    )
    query = _doctor_filter(query)
    tasks = query.order_by(_priority_ordering().asc(), CommercialTask.created_at.desc()).all()
    return [t for t in tasks if _task_has_cosmiatria_payload(t)]


def _list_week_tasks():
    today = date.today()
    start, end = monday_and_sunday()
    query = _base_derma_query().filter(
        CommercialTask.consultation_date >= start,
        CommercialTask.consultation_date <= end,
        CommercialTask.consultation_date < today,
        CommercialTask.status != 'fechado',
        CommercialTask.status != 'perdido',
    )
    query = _doctor_filter(query)
    tasks = query.order_by(_priority_ordering().asc(), CommercialTask.consultation_date.desc(), CommercialTask.created_at.desc()).all()
    return [t for t in tasks if _task_has_cosmiatria_payload(t)]


def _list_pending_tasks():
    start, _ = monday_and_sunday()
    query = _base_derma_query().filter(
        CommercialTask.status.in_(['novo', 'conversado', 'aguardando']),
        CommercialTask.consultation_date < start,
    )
    query = _doctor_filter(query)
    tasks = query.order_by(_priority_ordering().asc(), CommercialTask.updated_at.desc()).all()
    return [t for t in tasks if _task_has_cosmiatria_payload(t)]


@commercial_bp.route('/api/tasks/today')
@login_required
def get_today_tasks():
    _ensure_commercial_access()
    return jsonify([_serialize_task(t) for t in _list_today_tasks()])


@commercial_bp.route('/api/tasks/week')
@login_required
def get_week_tasks():
    _ensure_commercial_access()
    return jsonify([_serialize_task(t) for t in _list_week_tasks()])


@commercial_bp.route('/api/tasks/pending')
@login_required
def get_pending_tasks():
    _ensure_commercial_access()
    return jsonify([_serialize_task(t) for t in _list_pending_tasks()])


@commercial_bp.route('/api/task/<int:task_id>')
@login_required
def get_task(task_id):
    _ensure_commercial_access()
    task = CommercialTask.query.filter_by(id=task_id, source_type=DERMA_SOURCE_TYPE).first_or_404()
    if task.doctor_id not in _allowed_derma_doctor_ids() or not _task_has_cosmiatria_payload(task):
        abort(404)
    return jsonify(_serialize_task(task))


@commercial_bp.route('/api/task/<int:task_id>', methods=['PATCH'])
@login_required
def update_task(task_id):
    _ensure_commercial_access()
    task = CommercialTask.query.filter_by(id=task_id, source_type=DERMA_SOURCE_TYPE).first_or_404()
    if task.doctor_id not in _allowed_derma_doctor_ids():
        abort(404)

    payload = request.get_json(silent=True) or {}

    status = payload.get('status')
    if status and status in VALID_STATUSES:
        task.status = status

    priority = payload.get('priority')
    if priority and priority in VALID_PRIORITIES:
        task.priority = priority

    if 'seller_notes' in payload:
        task.seller_notes = (payload.get('seller_notes') or '').strip()

    followup = payload.get('next_followup_date')
    if followup is not None:
        task.next_followup_date = datetime.strptime(followup, '%Y-%m-%d').date() if followup else None

    if payload.get('mark_contacted'):
        task.last_contact_at = get_brazil_time()
        if task.status == 'novo':
            task.status = 'conversado'

    db.session.add(task)
    db.session.commit()
    return jsonify({'success': True, 'task': _serialize_task(task)})


@commercial_bp.route('/api/doctors')
@login_required
def get_doctors():
    _ensure_commercial_access()
    doctors = get_derma_dashboard_doctors()
    return jsonify([{'id': d.id, 'name': d.name} for d in doctors])


@commercial_bp.route('/api/v1/tasks/today')
@login_required
def get_today_tasks_alias():
    _ensure_commercial_access()
    return jsonify([_serialize_task(t) for t in _list_today_tasks()])


@commercial_bp.route('/api/v1/tasks/week')
@login_required
def get_week_tasks_alias():
    _ensure_commercial_access()
    return jsonify([_serialize_task(t) for t in _list_week_tasks()])


@commercial_bp.route('/api/v1/tasks/pending')
@login_required
def get_pending_tasks_alias():
    _ensure_commercial_access()
    return jsonify([_serialize_task(t) for t in _list_pending_tasks()])


@commercial_api_bp.route('/tasks/today')
@login_required
def api_today_tasks():
    _ensure_commercial_access()
    return jsonify([_serialize_task(t) for t in _list_today_tasks()])


@commercial_api_bp.route('/tasks/week')
@login_required
def api_week_tasks():
    _ensure_commercial_access()
    return jsonify([_serialize_task(t) for t in _list_week_tasks()])


@commercial_api_bp.route('/tasks/pending')
@login_required
def api_pending_tasks():
    _ensure_commercial_access()
    return jsonify([_serialize_task(t) for t in _list_pending_tasks()])


@commercial_api_bp.route('/task/<int:task_id>')
@login_required
def api_get_task(task_id):
    return get_task(task_id)


@commercial_api_bp.route('/task/<int:task_id>', methods=['PATCH'])
@login_required
def api_patch_task(task_id):
    return update_task(task_id)


@commercial_api_bp.route('/doctors')
@login_required
def api_get_doctors():
    return get_doctors()


@commercial_api_bp.route('/cp/readiness')
@login_required
def cp_readiness():
    """Preparação explícita para futuro dashboard CP, sem misturar no dashboard DERMA."""
    _ensure_commercial_access()
    cp_doctors = get_cp_doctors()
    cp_encounters = PlasticSurgeryEncounter.query.count()
    return jsonify({
        'cp_dashboard_ready': True,
        'cp_doctor_usernames': sorted(list(CP_DOCTOR_USERNAMES)),
        'cp_doctors': [{'id': d.id, 'name': d.name, 'username': d.username} for d in cp_doctors],
        'cp_encounters_count': cp_encounters,
        'derma_dashboard_doctor_usernames': sorted(list(DERMA_DASHBOARD_DOCTOR_USERNAMES)),
        'isolation_rule': 'Dashboard comercial atual consome somente source_type=derma e médicos permitidos de DERMA.',
    })
