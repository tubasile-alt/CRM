"""Rotas para registro de subscriptions Web Push do usuário autenticado."""
from flask import Blueprint, current_app, jsonify, request
from flask_login import current_user, login_required

from models import PushSubscription, db, get_brazil_time

push_bp = Blueprint('push', __name__, url_prefix='/api/push')


@push_bp.route('/vapid-public-key', methods=['GET'])
@login_required
def vapid_public_key():
    """Retorna somente a chave pública VAPID configurada."""
    public_key = current_app.config.get('VAPID_PUBLIC_KEY')
    if not public_key:
        return jsonify({'error': 'VAPID_PUBLIC_KEY não configurada'}), 503
    return jsonify({'publicKey': public_key})


@push_bp.route('/subscribe', methods=['POST'])
@login_required
def subscribe():
    """Cria ou atualiza a subscription Web Push para o usuário logado."""
    data = request.get_json(silent=True) or {}
    endpoint = data.get('endpoint')
    keys = data.get('keys') or {}
    p256dh = keys.get('p256dh')
    auth = keys.get('auth')

    if not endpoint or not p256dh or not auth:
        return jsonify({'error': 'Subscription inválida'}), 400

    subscription = PushSubscription.query.filter_by(
        user_id=current_user.id,
        endpoint=endpoint,
    ).first()

    now = get_brazil_time()
    if not subscription:
        subscription = PushSubscription(
            user_id=current_user.id,
            endpoint=endpoint,
            created_at=now,
        )

    subscription.p256dh = p256dh
    subscription.auth = auth
    subscription.user_agent = request.headers.get('User-Agent')
    subscription.last_seen_at = now
    subscription.is_active = True

    db.session.add(subscription)
    db.session.commit()

    return jsonify({'success': True, 'subscription_id': subscription.id})


@push_bp.route('/unsubscribe', methods=['POST'])
@login_required
def unsubscribe():
    """Marca uma subscription do usuário logado como inativa."""
    data = request.get_json(silent=True) or {}
    endpoint = data.get('endpoint')

    query = PushSubscription.query.filter_by(user_id=current_user.id, is_active=True)
    if endpoint:
        query = query.filter_by(endpoint=endpoint)

    updated = 0
    for subscription in query.all():
        subscription.is_active = False
        subscription.last_seen_at = get_brazil_time()
        db.session.add(subscription)
        updated += 1

    db.session.commit()
    return jsonify({'success': True, 'updated': updated})
