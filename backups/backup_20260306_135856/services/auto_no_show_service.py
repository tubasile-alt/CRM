"""
Servico de marcacao automatica de faltas
Verifica a cada X minutos se pacientes faltaram (30 min apos horario sem check-in)
"""
from datetime import datetime, timedelta, time
import pytz
from models import db, Appointment

TZ = pytz.timezone("America/Sao_Paulo")

def _now_sp_naive():
    """
    Retorna 'agora' em SP, mas SEM timezone (naive),
    para comparar com start_time salvo como naive no banco.
    """
    return datetime.now(TZ).replace(tzinfo=None)

def _today_sp():
    return datetime.now(TZ).date()

def mark_no_shows_grace_minutes(grace_minutes: int = 30):
    """
    Marca como 'faltou' SOMENTE agendamentos de HOJE que:
    - start_time <= agora - grace_minutes
    - checked_in_time IS NULL
    - waiting = False (nao esta na sala de espera)
    - status NOT IN ('atendido', 'faltou')
    """
    now_naive = _now_sp_naive()
    cutoff = now_naive - timedelta(minutes=grace_minutes)

    today = _today_sp()
    start_of_day = datetime.combine(today, time(0, 0, 0))
    end_of_day = datetime.combine(today, time(23, 59, 59))

    q = Appointment.query.filter(
        Appointment.start_time >= start_of_day,
        Appointment.start_time <= end_of_day,
        Appointment.start_time <= cutoff,
        Appointment.checked_in_time.is_(None),
        Appointment.waiting.is_(False),
        Appointment.status.notin_(["atendido", "faltou"])
    )

    appts = q.all()
    changed = 0

    for a in appts:
        a.status = "faltou"
        changed += 1

    if changed:
        db.session.commit()

    return changed
