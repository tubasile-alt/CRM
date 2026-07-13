"""Política temporal da Clínica Basile.
from datetime import datetime
from services.clinic_time import clinic_now
import pytz


Horários civis da agenda continuam sendo tratados como horários locais da
clínica. Instantes UTC, como check-in, são convertidos apenas na serialização;
nenhum valor existente no banco é reescrito.
"""

from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import pytz


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


def get_brazil_time():
    return clinic_now()

def parse_datetime_with_tz(iso_string):
    """Parse ISO datetime string - retorna naive datetime para São Paulo.
    NÃO usamos timezone para evitar conversões automáticas do SQLAlchemy."""
    # Remove 'Z' suffix if present and parse
    iso_string = iso_string.replace('Z', '')
    dt = datetime.fromisoformat(iso_string)
    
    # Sempre retorna naive (sem timezone) - representa horário de São Paulo
    if dt.tzinfo is not None:
        # Se veio com timezone, converter para São Paulo e remover tzinfo
        tz = pytz.timezone('America/Sao_Paulo')
        dt = dt.astimezone(tz).replace(tzinfo=None)
    
    return dt

def format_brazil_datetime(dt):
    """Converte datetime para timezone de São Paulo e formata"""
    if not dt:
        return None
    tz = pytz.timezone('America/Sao_Paulo')
    
    # Se o datetime é naive (sem timezone), assume que já está em São Paulo
    if dt.tzinfo is None:
        dt = tz.localize(dt)
    else:
        # Se tem timezone, converte para São Paulo
        dt = dt.astimezone(tz)
    
    return dt.strftime('%d/%m/%Y %H:%M')
