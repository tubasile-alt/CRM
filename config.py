import os
import logging
from datetime import timedelta

logger = logging.getLogger(__name__)


def _mask_db_url(url: str) -> str:
    """Return database URL with password replaced by ***."""
    if not url:
        return '(não definida)'
    try:
        from urllib.parse import urlparse, urlunparse
        parsed = urlparse(url)
        if parsed.password:
            masked = parsed._replace(
                netloc=f"{parsed.username}:***@{parsed.hostname}"
                + (f":{parsed.port}" if parsed.port else "")
            )
            return urlunparse(masked)
    except Exception:
        pass
    return url[:40] + '...(mascarada)'


def _build_engine_options(database_uri):
    if (database_uri or '').startswith('sqlite:'):
        return {}

    return {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
        'connect_args': {
            'connect_timeout': 10,
            'keepalives': 1,
            'keepalives_idle': 30,
        }
    }


def _resolve_database_url() -> str:
    """
    Select the correct DATABASE_URL based on environment.

    - Always prefer NEON_DATABASE_URL when set (shared between Preview and Production).
    - Fall back to DATABASE_URL (Replit internal helium) only when NEON_DATABASE_URL is absent.
    - Last resort: SQLite local.
    """
    is_production = os.environ.get('REPLIT_DEPLOYMENT', '0') == '1'
    env_label = 'PRODUÇÃO' if is_production else 'PREVIEW/DEV'

    url = (
        os.environ.get('NEON_DATABASE_URL')
        or os.environ.get('DATABASE_URL')
        or 'sqlite:///medcrm.db'
    )

    # Fix legacy postgres:// → postgresql://
    if url.startswith('postgres://'):
        url = 'postgresql://' + url[len('postgres://'):]

    print(f"[CONFIG] Ambiente: {env_label}")
    print(f"[CONFIG] DATABASE_URL em uso: {_mask_db_url(url)}")

    return url


IS_PRODUCTION = os.environ.get('REPLIT_DEPLOYMENT', '0') == '1'

_DB_URL = _resolve_database_url()


class Config:
    SECRET_KEY = os.environ.get('SESSION_SECRET') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = _DB_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = _build_engine_options(_DB_URL)
    TIMEZONE = 'America/Sao_Paulo'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=12)
    SESSION_COOKIE_SECURE = IS_PRODUCTION
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    WTF_CSRF_TIME_LIMIT = None

    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'clinicabasile@example.com')

    VAPID_PUBLIC_KEY = os.environ.get('VAPID_PUBLIC_KEY')
    VAPID_PRIVATE_KEY = os.environ.get('VAPID_PRIVATE_KEY')
    VAPID_CLAIMS_EMAIL = os.environ.get('VAPID_CLAIMS_EMAIL')

    DOCTOR_COLORS = ['#0d6efd', '#198754', '#dc3545', '#ffc107', '#6f42c1', '#20c997', '#fd7e14', '#0dcaf0']
    POLLING_INTERVAL = 30000
