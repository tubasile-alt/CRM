from flask import Blueprint, jsonify, request, abort
from flask_login import login_required, current_user
from models import db, PatientDoctor, PlasticSurgeryEncounter, PlasticSurgeryPlan, PlasticSurgeryBudget
from services.authz import require_dp_view, require_dp_edit, can_view_dp, can_edit_dp
from datetime import datetime

cp_bp = Blueprint('cp', __name__)


@cp_bp.route('/api/cp/encounter/start', methods=['POST'])
@login_required
def start_encounter():
    if current_user.is_secretary() or current_user.role_clinico == 'SECRETARY':
        abort(403)
    data = request.get_json() or {}
    dp_id = data.get('dp_id')
    if not dp_id:
        return jsonify({'error': 'dp_id obrigatório'}), 400

    dp = require_dp_view(dp_id)
    if not can_edit_dp(dp):
        abort(403)

    category = data.get('category', 'FACE')

    encounter = PlasticSurgeryEncounter(
        doctor_id=current_user.id,
        doctor_patient_id=dp.id,
        category=category,
        status='DRAFT'
    )
    db.session.add(encounter)
    db.session.flush()

    plan = PlasticSurgeryPlan(encounter_id=encounter.id)
    budget = PlasticSurgeryBudget(encounter_id=encounter.id, items={})
    db.session.add(plan)
    db.session.add(budget)
    db.session.commit()

    return jsonify({'encounter_id': encounter.id})


@cp_bp.route('/api/cp/encounter/<int:encounter_id>', methods=['GET'])
@login_required
def get_encounter(encounter_id):
    enc = PlasticSurgeryEncounter.query.get_or_404(encounter_id)
    dp = PatientDoctor.query.get(enc.doctor_patient_id)
    if not dp or not can_view_dp(dp):
        abort(403)

    plan = enc.plan
    budget = enc.budget

    return jsonify({
        'id': enc.id,
        'dp_id': enc.doctor_patient_id,
        'category': enc.category,
        'complaint_text': enc.complaint_text or '',
        'plan_summary_text': enc.plan_summary_text or '',
        'consultation_seconds': enc.consultation_seconds or 0,
        'status': enc.status,
        'updated_at': enc.updated_at.isoformat() if enc.updated_at else None,
        'plan': {
            'indication_status': plan.indication_status if plan else None,
            'case_type': plan.case_type if plan else None,
            'selected_procedures': plan.selected_procedures if plan else [],
            'lipo_areas': plan.lipo_areas if plan else [],
            'implant_plane': plan.implant_plane if plan else '',
            'implant_profile': plan.implant_profile if plan else '',
            'implant_volume_min': plan.implant_volume_min if plan else None,
            'implant_volume_max': plan.implant_volume_max if plan else None,
            'technologies': plan.technologies if plan else [],
            'internacao': plan.internacao if plan else '',
            'estimated_time': plan.estimated_time if plan else '',
            'follow_up_deadline': plan.follow_up_deadline if plan else '',
            'reception_obs': plan.reception_obs if plan else '',
        } if plan else {},
        'budget': {
            'items': budget.items if budget else {},
            'all_in_price': budget.all_in_price if budget else None,
            'currency': budget.currency if budget else 'BRL',
        } if budget else {}
    })


@cp_bp.route('/api/cp/encounter/<int:encounter_id>/save', methods=['POST'])
@login_required
def save_encounter(encounter_id):
    enc = PlasticSurgeryEncounter.query.get_or_404(encounter_id)
    dp = PatientDoctor.query.get(enc.doctor_patient_id)
    if not dp or not can_edit_dp(dp):
        abort(403)

    data = request.get_json() or {}

    if 'category' in data:
        enc.category = data['category']
    if 'complaint_text' in data:
        enc.complaint_text = data['complaint_text']
    if 'plan_summary_text' in data:
        enc.plan_summary_text = data['plan_summary_text']
    if 'consultation_seconds' in data:
        enc.consultation_seconds = data['consultation_seconds']
    if 'status' in data:
        enc.status = data['status']

    plan_data = data.get('plan', {})
    if plan_data:
        plan = enc.plan
        if not plan:
            plan = PlasticSurgeryPlan(encounter_id=enc.id)
            db.session.add(plan)
        for field in ('indication_status', 'case_type', 'selected_procedures', 'lipo_areas',
                      'implant_plane', 'implant_profile', 'implant_volume_min', 'implant_volume_max',
                      'technologies', 'internacao', 'estimated_time', 'follow_up_deadline', 'reception_obs'):
            if field in plan_data:
                setattr(plan, field, plan_data[field])

    budget_data = data.get('budget', {})
    if budget_data:
        budget = enc.budget
        if not budget:
            budget = PlasticSurgeryBudget(encounter_id=enc.id)
            db.session.add(budget)
        if 'items' in budget_data:
            budget.items = budget_data['items']
        if 'all_in_price' in budget_data:
            budget.all_in_price = budget_data['all_in_price']

    db.session.commit()
    return jsonify({'ok': True, 'saved_at': datetime.utcnow().isoformat()})


@cp_bp.route('/api/cp/patient/<int:dp_id>/history', methods=['GET'])
@login_required
def get_patient_history(dp_id):
    dp = require_dp_view(dp_id)

    encounters = PlasticSurgeryEncounter.query\
        .filter_by(doctor_patient_id=dp.id)\
        .order_by(PlasticSurgeryEncounter.created_at.desc())\
        .all()

    result = []
    for enc in encounters:
        result.append({
            'id': enc.id,
            'category': enc.category,
            'status': enc.status,
            'complaint_text': (enc.complaint_text or '')[:120],
            'plan_summary_text': (enc.plan_summary_text or '')[:120],
            'created_at': enc.created_at.isoformat() if enc.created_at else None,
            'updated_at': enc.updated_at.isoformat() if enc.updated_at else None,
        })

    return jsonify(result)


@cp_bp.route('/api/cp/encounter/<int:encounter_id>/finalize', methods=['POST'])
@login_required
def finalize_encounter(encounter_id):
    enc = PlasticSurgeryEncounter.query.get_or_404(encounter_id)
    dp = PatientDoctor.query.get(enc.doctor_patient_id)
    if not dp or not can_edit_dp(dp):
        abort(403)
    enc.status = 'FINAL'
    db.session.commit()
    return jsonify({'ok': True})


@cp_bp.route('/api/cp/exam-request/<int:encounter_id>', methods=['GET'])
@login_required
def exam_request_stub(encounter_id):
    return jsonify({'error': 'Funcionalidade de impressão não implementada nesta versão'}), 501


@cp_bp.route('/api/cp/tcle/<int:encounter_id>', methods=['GET'])
@login_required
def tcle_stub(encounter_id):
    return jsonify({'error': 'Funcionalidade de TCLE não implementada nesta versão'}), 501
