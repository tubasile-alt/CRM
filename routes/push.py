"""Rotas para registro de subscriptions Web Push do usuário autenticado."""
import logging

from flask import Blueprint, current_app, jsonify, request
from flask_login import current_user, login_required

from models import PushSubscription, db, get_brazil_time
from services.push_schema_service import ensure_push_subscription_schema

push_bp = Blueprint('push', __name__, url_prefix='/api/push')
logger = logging.getLogger(__name__)


@push_bp.before_request
def ensure_push_storage():
    if request.endpoint == 'push.vapid_public_key':
        return None

    try:
        ensure_push_subscription_schema()
    except Exception:
        logger.exception('Não foi possível preparar o armazenamento de Web Push.')
        return jsonify({
            'success': False,
            'code': 'push_storage_unavailable',
            'error': 'Banco de notificações indisponível. Publique novamente e tente de novo.',
        }), 503

    return None


def _endpoint_partial(endpoint):
    if not endpoint:
        return None
    if len(endpoint) <= 60:
        return endpoint
    return f'{endpoint[:36]}...{endpoint[-20:]}'


def _detect_platform(user_agent):
    ua = (user_agent or '').lower()
    if 'iphone' in ua:
        return 'iphone'
    if 'ipad' in ua or ('macintosh' in ua and 'mobile' in ua):
        return 'ipad'
    if 'android' in ua:
        return 'android'
    if 'mac os' in ua or 'macintosh' in ua:
        return 'macos'
    if 'windows' in ua:
        return 'windows'
    return 'web'


def _subscription_payload(subscription):
    if not subscription:
        return None
    return {
        'id': subscription.id,
        'platform': subscription.platform,
        'endpoint_partial': subscription.endpoint_partial,
        'last_seen_at': subscription.last_seen_at.isoformat() if subscription.last_seen_at else None,
        'last_test_at': subscription.last_test_at.isoformat() if subscription.last_test_at else None,
        'last_error': subscription.last_error,
        'is_active': subscription.is_active,
    }


@push_bp.route('/vapid-public-key', methods=['GET'])
def vapid_public_key():
    """Retorna somente a chave pública VAPID configurada.

    A chave pública VAPID é segura para ser exposta publicamente;
    o service worker precisa acessá-la sem sessão de login.
    """
    public_key = current_app.config.get('VAPID_PUBLIC_KEY')
    if not public_key:
        return jsonify({'error': 'VAPID_PUBLIC_KEY não configurada'}), 503
    return jsonify({'publicKey': public_key})


@push_bp.route('/status', methods=['GET'])
@login_required
def status():
    """Retorna o estado mais recente de push para o usuário logado."""
    subscription = PushSubscription.query.filter_by(
        user_id=current_user.id,
        is_active=True,
    ).order_by(PushSubscription.last_seen_at.desc()).first()

    return jsonify({
        'success': True,
        'has_subscription': bool(subscription),
        'subscription': _subscription_payload(subscription),
    })


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
    user_agent = request.headers.get('User-Agent')
    subscription.user_agent = user_agent
    subscription.platform = _detect_platform(user_agent)
    subscription.endpoint_partial = _endpoint_partial(endpoint)
    subscription.last_seen_at = now
    subscription.last_error = None
    subscription.is_active = True

    db.session.add(subscription)
    db.session.commit()

    return jsonify({'success': True, 'subscription_id': subscription.id, 'subscription': _subscription_payload(subscription)})


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


@push_bp.route('/test', methods=['POST'])
@login_required
def test_push():
    """Envia uma notificação push de teste para o usuário logado."""
    from services.push_service import send_checkin_push_notification
    result = send_checkin_push_notification(
        doctor_id=current_user.id,
        patient_name='Teste de Notificação',
        appointment_id=999,
        patient_id=999,
    )
    now = get_brazil_time()
    active_subscriptions = PushSubscription.query.filter_by(
        user_id=current_user.id,
        is_active=True,
    ).all()
    for subscription in active_subscriptions:
        subscription.last_test_at = now
        db.session.add(subscription)
    db.session.commit()

    latest = PushSubscription.query.filter_by(
        user_id=current_user.id,
        is_active=True,
    ).order_by(PushSubscription.last_seen_at.desc()).first()
    response = {
        'success': result.get('sent', 0) > 0,
        'result': result,
        'subscription': _subscription_payload(latest),
    }
    if result.get('skipped'):
        response['error'] = result.get('error') or 'Configuração VAPID incompleta.'
        return jsonify(response), 503
    if result.get('failed', 0) > 0 and result.get('sent', 0) == 0:
        response['error'] = (
            latest.last_error if latest and latest.last_error
            else 'O provedor push recusou a notificação.'
        )
        return jsonify(response), 502
    return jsonify(response)
