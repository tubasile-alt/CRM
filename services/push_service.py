"""Serviço de notificações push Web Push para eventos do CRM."""
import json
import logging

from flask import current_app
from models import PushSubscription, db

logger = logging.getLogger(__name__)


def _vapid_claims():
    email = current_app.config.get('VAPID_CLAIMS_EMAIL')
    if not email:
        return None

    email = email.strip()
    if email.lower().startswith('mailto:'):
        email = email.split(':', 1)[1].strip()
    subject = f'mailto:{email}'
    import time
    return {'sub': subject, 'exp': int(time.time()) + 86400}


def _subscription_info(subscription):
    return {
        'endpoint': subscription.endpoint,
        'keys': {
            'p256dh': subscription.p256dh,
            'auth': subscription.auth,
        },
    }


def _mark_subscription_inactive(subscription):
    subscription.is_active = False
    db.session.add(subscription)
    db.session.commit()


def _set_subscription_error(subscription, message):
    subscription.last_error = (message or 'Erro desconhecido')[:1000]
    db.session.add(subscription)


def _clear_subscription_error(subscription):
    subscription.last_error = None
    db.session.add(subscription)


def send_checkin_push_notification(doctor_id, patient_name, appointment_id, patient_id=None):
    """Envia push para o médico quando um paciente faz check-in.

    Compatibilidade iPhone/PWA:
    - No iPhone, Web Push exige iOS 16.4+.
    - O CRM precisa estar adicionado à Tela de Início.
    - O usuário precisa permitir notificações.
    - O ambiente precisa estar em HTTPS.

    Falhas de push são registradas e não devem interromper o fluxo de check-in.
    """
    public_key = current_app.config.get('VAPID_PUBLIC_KEY')
    private_key = current_app.config.get('VAPID_PRIVATE_KEY')
    claims = _vapid_claims()

    if not public_key or not private_key or not claims:
        logger.warning('Push de check-in ignorado: configuração VAPID incompleta.')
        missing = []
        if not public_key:
            missing.append('VAPID_PUBLIC_KEY')
        if not private_key:
            missing.append('VAPID_PRIVATE_KEY')
        if not claims:
            missing.append('VAPID_CLAIMS_EMAIL')
        return {
            'sent': 0,
            'failed': 0,
            'skipped': True,
            'error': f"Configuração VAPID incompleta: {', '.join(missing)}.",
        }

    subscriptions = PushSubscription.query.filter_by(
        user_id=doctor_id,
        is_active=True,
    ).all()

    if not subscriptions:
        return {'sent': 0, 'failed': 0, 'skipped': False}

    from pywebpush import WebPushException, webpush

    patient_name = patient_name or 'Paciente'
    payload = {
        'title': 'Paciente chegou',
        'body': f'{patient_name} fez check-in',
        'icon': '/icon-192.png',
        'badge': '/icon-192.png',
        'data': {
            'url': f'/prontuario/{patient_id}?appointment_id={appointment_id}' if patient_id else '/agenda',
            'appointment_id': appointment_id,
            'patient_id': patient_id,
        },
    }

    sent = 0
    failed = 0
    for subscription in subscriptions:
        try:
            webpush(
                subscription_info=_subscription_info(subscription),
                data=json.dumps(payload),
                vapid_private_key=private_key,
                vapid_claims=claims,
            )
            _clear_subscription_error(subscription)
            sent += 1
        except WebPushException as exc:
            failed += 1
            status_code = getattr(getattr(exc, 'response', None), 'status_code', None)
            _set_subscription_error(subscription, f'WebPushException status={status_code}: {exc}')
            if status_code in (404, 410):
                _mark_subscription_inactive(subscription)
            else:
                db.session.commit()
            logger.exception(
                'Falha ao enviar push de check-in para user_id=%s subscription_id=%s',
                doctor_id,
                subscription.id,
            )
        except Exception as exc:
            failed += 1
            _set_subscription_error(subscription, str(exc))
            db.session.commit()
            logger.exception(
                'Erro inesperado ao enviar push de check-in para user_id=%s subscription_id=%s',
                doctor_id,
                subscription.id,
            )

    if sent:
        db.session.commit()

    return {'sent': sent, 'failed': failed, 'skipped': False}
