"""
Servico de marcacao automatica de faltas.

Pacientes provisorios sao marcados como faltou logo apos a tolerancia, porque
nao fazem check-in nem recebem prontuario real antes da ativacao. Pacientes
ativos preservam a regra historica: apenas apos o fim do horario comercial.
"""
from datetime import datetime, timedelta, time
import pytz
from models import db, Appointment, Patient
from services.statuses import AppointmentStatus, appointment_pending_status_values

TZ = pytz.timezone("America/Sao_Paulo")

BUSINESS_HOURS_END = time(19, 0)


def _now_sp():
    return datetime.now(TZ)


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
    - status ainda permite falta automatica

    Pacientes ativos so entram apos as 19h. Pacientes provisorios entram
    imediatamente apos a tolerancia de 30 minutos.
    """
    now_sp = _now_sp()

    now_naive = now_sp.replace(tzinfo=None)
    cutoff = now_naive - timedelta(minutes=grace_minutes)

    today = _today_sp()
    start_of_day = datetime.combine(today, time(0, 0, 0))
    end_of_day = datetime.combine(today, time(23, 59, 59))

    eligible_statuses = appointment_pending_status_values(include_aliases=True)

    base_q = Appointment.query.join(Patient, Appointment.patient_id == Patient.id).filter(
        Appointment.start_time >= start_of_day,
        Appointment.start_time <= end_of_day,
        Appointment.start_time <= cutoff,
        Appointment.checked_in_time.is_(None),
        Appointment.waiting.is_(False),
        Appointment.status.in_(eligible_statuses),
    )

    filters = [Patient.status_cadastral == "provisorio"]
    if now_sp.time() >= BUSINESS_HOURS_END:
        filters.append(Patient.status_cadastral != "provisorio")

    appts = base_q.filter(db.or_(*filters)).all()
    changed = 0

    for a in appts:
        a.status = AppointmentStatus.NO_SHOW
        changed += 1

    if changed:
        db.session.commit()

    return changed
