from flask import Blueprint, current_app as app, jsonify, request
from flask_login import current_user, login_required

from models import Appointment, Payment, db
from services.clinic_time import format_brazil_datetime, get_brazil_time
from services.pricing import CONSULTATION_PRICES


checkout_api_bp = Blueprint('checkout_api', __name__)


@checkout_api_bp.route('/api/checkout/pending', methods=['GET'])
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
        _ = consultation_fee
        
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


@checkout_api_bp.route('/api/checkout/create', methods=['POST'])
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


@checkout_api_bp.route('/api/checkout/<int:payment_id>/pay', methods=['POST'])
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


@checkout_api_bp.route('/api/checkout/pending/count', methods=['GET'])
@login_required
def get_pending_checkout_count():
    """Retorna a contagem de checkouts pendentes do dia"""
    today = get_brazil_time().date()
    
    count = Payment.query.filter(
        db.func.date(Payment.created_at) == today,
        Payment.status == 'pendente'
    ).count()
    
    return jsonify({'success': True, 'count': count})


@checkout_api_bp.route('/api/checkout/<int:payment_id>/toggle-consultation', methods=['POST'])
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
