"""Política temporal da Clínica Basile.

Horários civis da agenda continuam sendo tratados como horários locais da
clínica. Instantes UTC, como check-in, são convertidos apenas na serialização;
nenhum valor existente no banco é reescrito.
"""

from datetime import datetime, timezone
from zoneinfo import ZoneInfo


CLINIC_TIMEZONE_NAME = 'America/Sao_Paulo'
CLINIC_TIMEZONE = ZoneInfo(CLINIC_TIMEZONE_NAME)


def clinic_now():
    """Retorna o instante atual no timezone de Ribeirão Preto/São Paulo."""
    return datetime.now(CLINIC_TIMEZONE)


def clinic_today():
    """Retorna a data civil corrente da clínica, independente do servidor."""
    return clinic_now().date()


def clinic_wall_time_iso(value):
    """Serializa um horário civil da clínica sem alterar sua hora de relógio."""
    if value is None:
        return None
    if value.tzinfo is None:
        value = value.replace(tzinfo=CLINIC_TIMEZONE)
    else:
        value = value.astimezone(CLINIC_TIMEZONE)
    return value.isoformat()


def utc_instant_to_clinic_iso(value):
    """Serializa um instante UTC em São Paulo; valores naive são UTC legados."""
    if value is None:
        return None
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(CLINIC_TIMEZONE).isoformat()
