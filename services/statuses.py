"""Vocabulários de estado por domínio, sem alterar dados persistidos."""


class AppointmentStatus:
    SCHEDULED = 'agendado'
    CONFIRMED = 'confirmado'
    COMPLETED = 'atendido'
    NO_SHOW = 'faltou'
    CANCELLED = 'cancelado'

    CANONICAL = frozenset({SCHEDULED, CONFIRMED, COMPLETED, NO_SHOW, CANCELLED})
    ALIASES = {
        'agendada': SCHEDULED,
        'confirmada': CONFIRMED,
        'atendida': COMPLETED,
        'cancelada': CANCELLED,
    }


class SurgeryStatus:
    SCHEDULED = 'agendada'
    CANCELLED = 'cancelada'


class ExecutionStatus:
    SCHEDULED = 'agendada'
    COMPLETED = 'realizada'
    CANCELLED = 'cancelada'
    NO_SHOW = 'faltou'


class ExecutionFollowUpStatus:
    PENDING = 'pendente'
    CONTACTED = 'contatado'
    SCHEDULED = 'agendado'
    NO_RESPONSE = 'sem_resposta'


class PaymentStatus:
    PENDING = 'pendente'
    PAID = 'pago'
    CANCELLED = 'cancelado'


class PatientRegistrationStatus:
    ACTIVE = 'ativo'
    PROVISIONAL = 'provisorio'


class EncounterStatus:
    DRAFT = 'DRAFT'
    FINAL = 'FINAL'


def normalize_appointment_status(value, default=AppointmentStatus.SCHEDULED):
    """Normaliza aliases conhecidos em memória e preserva valores desconhecidos."""
    if value is None or not str(value).strip():
        return default

    normalized = str(value).strip().lower()
    return AppointmentStatus.ALIASES.get(normalized, normalized)


def appointment_status_values(include_aliases=False):
    values = set(AppointmentStatus.CANONICAL)
    if include_aliases:
        values.update(AppointmentStatus.ALIASES)
    return frozenset(values)


def appointment_pending_status_values(include_aliases=False):
    values = {AppointmentStatus.SCHEDULED, AppointmentStatus.CONFIRMED}
    if include_aliases:
        values.update(
            alias for alias, canonical in AppointmentStatus.ALIASES.items()
            if canonical in values
        )
    return frozenset(values)
