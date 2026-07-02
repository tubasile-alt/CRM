"""Prévia e importação transacional de linhas da agenda física."""
from datetime import datetime, timedelta

from models import Appointment, Patient, PatientDoctor, PhysicalAgendaImportLog, db
from services.physical_agenda_schema_service import ensure_physical_agenda_import_schema
from services.statuses import AppointmentStatus, normalize_appointment_status


MAX_IMPORT_ITEMS = 100
MIN_DURATION_MINUTES = 5
MAX_DURATION_MINUTES = 480
DEFAULT_DURATION_MINUTES = 5
SLOT_MINUTES = 5


class PhysicalAgendaImportError(ValueError):
    pass


def _clean_text(value, max_length=None):
    text = ' '.join(str(value or '').split()).strip()
    if max_length and len(text) > max_length:
        raise PhysicalAgendaImportError(f'Texto excede {max_length} caracteres.')
    return text


def _parse_item(item, row_index):
    if not isinstance(item, dict):
        raise PhysicalAgendaImportError('Linha inválida.')

    try:
        patient_id = int(item.get('patient_id') or '')
    except (TypeError, ValueError) as exc:
        raise PhysicalAgendaImportError('Selecione um paciente para esta linha.') from exc

    agenda_date = _clean_text(item.get('agenda_date'), 10)
    time_value = _clean_text(item.get('time'), 5)
    try:
        start_time = datetime.strptime(f'{agenda_date} {time_value}', '%Y-%m-%d %H:%M')
    except ValueError as exc:
        raise PhysicalAgendaImportError('Data ou horário inválido.') from exc

    try:
        duration = int(item.get('duration_minutes') or DEFAULT_DURATION_MINUTES)
    except (TypeError, ValueError) as exc:
        raise PhysicalAgendaImportError('Duração inválida.') from exc
    if not MIN_DURATION_MINUTES <= duration <= MAX_DURATION_MINUTES:
        raise PhysicalAgendaImportError('A duração deve ficar entre 5 e 480 minutos.')

    appointment_type = _clean_text(item.get('appointment_type') or 'Particular', 20)
    procedure = _clean_text(item.get('procedure'), 200)
    notes = _clean_text(item.get('notes'), 2000)
    idempotency_key = _clean_text(item.get('idempotency_key'), 64)
    if len(idempotency_key) < 16:
        raise PhysicalAgendaImportError('Identificador de importação inválido.')

    return {
        'row_index': row_index,
        'patient_id': patient_id,
        'agenda_date': agenda_date,
        'start_time': start_time,
        'end_time': start_time + timedelta(minutes=duration),
        'duration_minutes': duration,
        'appointment_type': appointment_type,
        'procedure': procedure,
        'notes': notes,
        'idempotency_key': idempotency_key,
        'issues': [],
        'conflicts': [],
    }


def _serialize_conflict(appointment):
    return {
        'appointment_id': appointment.id,
        'start': appointment.start_time.isoformat(timespec='minutes'),
        'end': appointment.end_time.isoformat(timespec='minutes'),
        'patient_name': appointment.patient.name if appointment.patient else 'Paciente',
        'status': normalize_appointment_status(appointment.status),
    }


def _floor_to_slot(value):
    minute = value.minute - (value.minute % SLOT_MINUTES)
    return value.replace(minute=minute, second=0, microsecond=0)


def _overlaps(start_time, end_time, interval):
    return interval['start'] < end_time and interval['end'] > start_time


def build_import_preview(items, doctor_id):
    """Valida pacientes e sobreposições sem alterar o banco."""
    ensure_physical_agenda_import_schema()
    if not isinstance(items, list) or not items:
        raise PhysicalAgendaImportError('Selecione ao menos uma linha para importar.')
    if len(items) > MAX_IMPORT_ITEMS:
        raise PhysicalAgendaImportError(f'O lote aceita até {MAX_IMPORT_ITEMS} linhas.')

    rows = []
    for index, item in enumerate(items):
        try:
            rows.append(_parse_item(item, index))
        except PhysicalAgendaImportError as exc:
            rows.append({
                'row_index': index,
                'issues': [str(exc)],
                'conflicts': [],
                'idempotency_key': str(item.get('idempotency_key') or '') if isinstance(item, dict) else '',
            })

    parsed_rows = [row for row in rows if 'start_time' in row]
    keys_seen = set()
    for row in parsed_rows:
        if row['idempotency_key'] in keys_seen:
            row['issues'].append('Identificador de importação repetido no lote.')
        keys_seen.add(row['idempotency_key'])

    patient_ids = {row['patient_id'] for row in parsed_rows}
    patients = Patient.query.filter(Patient.id.in_(patient_ids)).all() if patient_ids else []
    patients_by_id = {patient.id: patient for patient in patients}
    links = PatientDoctor.query.filter(
        PatientDoctor.patient_id.in_(patient_ids),
        PatientDoctor.doctor_id == doctor_id,
    ).all() if patient_ids else []
    linked_patient_ids = {link.patient_id for link in links}

    for row in parsed_rows:
        patient = patients_by_id.get(row['patient_id'])
        if not patient:
            row['issues'].append('Paciente não encontrado.')
            continue
        if patient.status_cadastral not in {'ativo', 'provisorio'}:
            row['issues'].append('Situação cadastral do paciente não permite agendamento.')
        if patient.status_cadastral == 'provisorio' and patient.id not in linked_patient_ids:
            row['issues'].append('Paciente provisório não pertence ao médico selecionado.')
        row['patient_name'] = patient.name
        row['patient_status'] = patient.status_cadastral

    if parsed_rows:
        first_date = min(row['start_time'].date() for row in parsed_rows)
        last_date = max(row['start_time'].date() for row in parsed_rows)
        window_start = datetime.combine(first_date, datetime.min.time())
        window_end = datetime.combine(last_date + timedelta(days=1), datetime.min.time())
        existing_appointments = Appointment.query.filter(
            Appointment.doctor_id == doctor_id,
            Appointment.start_time < window_end,
            Appointment.end_time > window_start,
        ).all()
        existing_appointments = [
            appointment for appointment in existing_appointments
            if normalize_appointment_status(appointment.status) != AppointmentStatus.CANCELLED
        ]
    else:
        existing_appointments = []

    existing_keys = {
        log.idempotency_key: log
        for log in PhysicalAgendaImportLog.query.filter(
            PhysicalAgendaImportLog.idempotency_key.in_(
                [row['idempotency_key'] for row in parsed_rows]
            )
        ).all()
    } if parsed_rows else {}

    for row in parsed_rows:
        prior_log = existing_keys.get(row['idempotency_key'])
        if prior_log:
            row['issues'].append('Esta linha já foi importada.')
            row['existing_appointment_id'] = prior_log.appointment_id

    occupied = [
        {
            'start': appointment.start_time,
            'end': appointment.end_time,
            'appointment': appointment,
        }
        for appointment in existing_appointments
    ]
    for row in sorted(parsed_rows, key=lambda item: (item['start_time'], item['row_index'])):
        if row['issues']:
            continue

        requested_start = row['start_time']
        proposed_start = _floor_to_slot(requested_start)
        proposed_end = proposed_start + timedelta(minutes=row['duration_minutes'])
        encountered_appointments = {}

        while True:
            collisions = [
                interval for interval in occupied
                if _overlaps(proposed_start, proposed_end, interval)
            ]
            if not collisions:
                break
            for interval in collisions:
                appointment = interval.get('appointment')
                if appointment:
                    encountered_appointments[appointment.id] = appointment
            proposed_start += timedelta(minutes=SLOT_MINUTES)
            proposed_end = proposed_start + timedelta(minutes=row['duration_minutes'])
            if proposed_start.date() != requested_start.date():
                row['issues'].append('Não há espaço livre neste dia para encaixar o horário.')
                break

        row['requested_start_time'] = requested_start
        row['start_time'] = proposed_start
        row['end_time'] = proposed_end
        row['adjusted'] = proposed_start != requested_start
        row['conflicts'] = [
            _serialize_conflict(appointment)
            for appointment in encountered_appointments.values()
        ]
        if not row['issues']:
            occupied.append({'start': proposed_start, 'end': proposed_end, 'appointment': None})

    response_rows = []
    for row in rows:
        conflicts = row.get('conflicts', [])
        issues = list(dict.fromkeys(row.get('issues', [])))
        response_rows.append({
            'row_index': row['row_index'],
            'ready': not issues,
            'patient_id': row.get('patient_id'),
            'patient_name': row.get('patient_name'),
            'patient_status': row.get('patient_status'),
            'start': row.get('start_time').isoformat(timespec='minutes') if row.get('start_time') else None,
            'end': row.get('end_time').isoformat(timespec='minutes') if row.get('end_time') else None,
            'requested_start': (
                row.get('requested_start_time').isoformat(timespec='minutes')
                if row.get('requested_start_time') else None
            ),
            'adjusted': bool(row.get('adjusted')),
            'issues': issues,
            'conflicts': conflicts,
            'existing_appointment_id': row.get('existing_appointment_id'),
        })

    return {
        'ready': all(row['ready'] for row in response_rows),
        'rows': response_rows,
        'normalized_rows': parsed_rows,
    }


def _appointment_notes(row):
    parts = []
    if row['procedure']:
        parts.append(f'Procedimento: {row["procedure"]}')
    if row['notes']:
        parts.append(row['notes'])
    return '\n'.join(parts)


def import_appointments(items, doctor_id, performed_by_user_id):
    """Revalida e cria o lote inteiro em uma única transação."""
    if db.engine.dialect.name == 'postgresql':
        db.session.execute(db.text('LOCK TABLE appointment IN SHARE ROW EXCLUSIVE MODE'))

    preview = build_import_preview(items, doctor_id)
    if not preview['ready']:
        return None, preview

    normalized_rows = preview['normalized_rows']
    patient_ids = {row['patient_id'] for row in normalized_rows}
    patients = Patient.query.filter(Patient.id.in_(patient_ids)).all()
    patients_by_id = {patient.id: patient for patient in patients}
    links = PatientDoctor.query.filter(
        PatientDoctor.patient_id.in_(patient_ids),
        PatientDoctor.doctor_id == doctor_id,
    ).all()
    linked_patient_ids = {link.patient_id for link in links}
    next_code = None

    created = []
    for row in normalized_rows:
        patient = patients_by_id[row['patient_id']]
        if patient.id not in linked_patient_ids:
            if patient.status_cadastral != 'ativo':
                raise PhysicalAgendaImportError('Vínculo inválido para paciente provisório.')
            if next_code is None:
                max_code = db.session.query(db.func.max(PatientDoctor.patient_code)).filter(
                    PatientDoctor.doctor_id == doctor_id,
                ).scalar() or 1000
                next_code = max(1001, max_code + 1)
            db.session.add(PatientDoctor(
                patient_id=patient.id,
                doctor_id=doctor_id,
                patient_code=next_code,
            ))
            linked_patient_ids.add(patient.id)
            next_code += 1

        appointment = Appointment(
            patient_id=patient.id,
            doctor_id=doctor_id,
            start_time=row['start_time'],
            end_time=row['end_time'],
            status=AppointmentStatus.SCHEDULED,
            appointment_type=row['appointment_type'],
            notes=_appointment_notes(row),
        )
        db.session.add(appointment)
        db.session.flush()
        db.session.add(PhysicalAgendaImportLog(
            idempotency_key=row['idempotency_key'],
            appointment_id=appointment.id,
            doctor_id=doctor_id,
            patient_id=patient.id,
            performed_by_user_id=performed_by_user_id,
            source_date=row['start_time'].date(),
        ))
        created.append({
            'row_index': row['row_index'],
            'appointment_id': appointment.id,
            'patient_id': patient.id,
            'start': appointment.start_time.isoformat(timespec='minutes'),
            'end': appointment.end_time.isoformat(timespec='minutes'),
        })

    db.session.commit()
    return created, preview
