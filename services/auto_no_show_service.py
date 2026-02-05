"""
Servico de marcacao automatica de faltas
Verifica a cada X minutos se pacientes faltaram (30 min apos horario sem check-in)
"""
from datetime import datetime, timedelta
import pytz
from models import db, Appointment

TZ = pytz.timezone("America/Sao_Paulo")

def _now_sp():
    return datetime.now(TZ)

def mark_no_shows_grace_minutes(grace_minutes: int = 30):
    """
    Marca como 'faltou' todos os agendamentos do dia que:
    - start_time <= agora - grace_minutes
    - checked_in_time IS NULL
    - status NOT IN ('atendido', 'faltou', 'cancelado')
    - waiting = False (nao esta na sala de espera)
    """
    now = _now_sp()
    cutoff = now - timedelta(minutes=grace_minutes)
    today = now.date()

    q = Appointment.query.filter(
        db.func.date(Appointment.start_time) == today,
        Appointment.start_time <= cutoff,
        Appointment.checked_in_time.is_(None),
        Appointment.waiting == False,
        Appointment.status.notin_(["atendido", "faltou", "cancelado"])
    )

    appts = q.all()
    changed = 0

    for a in appts:
        a.status = "faltou"
        changed += 1

    if changed:
        db.session.commit()

    return changed
