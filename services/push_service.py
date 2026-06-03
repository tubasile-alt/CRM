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

    subject = email if email.startswith('mailto:') else f'mailto:{email}'
    return {'sub': subject}


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
        return {'sent': 0, 'failed': 0, 'skipped': True}

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
            sent += 1
        except WebPushException as exc:
            failed += 1
            status_code = getattr(getattr(exc, 'response', None), 'status_code', None)
            if status_code in (404, 410):
                _mark_subscription_inactive(subscription)
            logger.exception(
                'Falha ao enviar push de check-in para user_id=%s subscription_id=%s',
                doctor_id,
                subscription.id,
            )
        except Exception:
            failed += 1
            logger.exception(
                'Erro inesperado ao enviar push de check-in para user_id=%s subscription_id=%s',
                doctor_id,
                subscription.id,
            )

    return {'sent': sent, 'failed': failed, 'skipped': False}
