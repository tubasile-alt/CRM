"""Prévia e importação transacional de linhas da agenda física."""
from datetime import datetime, timedelta

from models import Appointment, Patient, PatientDoctor, PhysicalAgendaImportLog, db
from services.physical_agenda_matching import (
    find_equivalent_provisional,
    normalize_phone,
    suggest_active_patients,
)
from services.physical_agenda_schema_service import ensure_physical_agenda_import_schema
from services.statuses import AppointmentStatus, normalize_appointment_status


MAX_IMPORT_ITEMS = 100
DEFAULT_DURATION_MINUTES = 5
SLOT_MINUTES = 5
MIN_DURATION_MINUTES = 5
MAX_DURATION_MINUTES = 480


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
        'patient_id': item.get('patient_id'),
        'patient_name': _clean_text(item.get('patient_name'), 100),
        'phone': _clean_text(item.get('phone'), 20),
        'cpf': _clean_text(item.get('cpf'), 14),
        'patient_code': _clean_text(item.get('patient_code'), 20),
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


def _resolve_or_create_patient(item, doctor_id, next_code):
    """Resolve paciente: usa seleção explícita, auto-match forte, provisório existente, ou cria provisório novo."""
    patient_name = item.get('patient_name')
    phone = item.get('phone')
    cpf = item.get('cpf')
    patient_code = item.get('patient_code')
    phone_digits = normalize_phone(phone)
    if not patient_code and 1 <= len(phone_digits) <= 6:
        patient_code = phone_digits

    # 1) Paciente explicitamente selecionado pelo usuário no frontend
    explicit_patient_id = item.get('patient_id')
    if explicit_patient_id:
        patient = db.session.get(Patient, int(explicit_patient_id))
        if patient and patient.status_cadastral in {'ativo', 'provisorio'}:
            status = 'ativo_selecionado' if patient.status_cadastral == 'ativo' else 'provisorio_selecionado'
            return patient, status, next_code

    if not patient_name:
        return None, None, next_code

    # 2) Buscar ativo com match forte (score >= 0.9)
    suggestions = suggest_active_patients(
        patient_name,
        phone,
        doctor_id,
        cpf=cpf,
        patient_code=patient_code,
        limit=5,
    )
    strong_match = suggestions[0] if suggestions and suggestions[0]['score'] >= 0.9 else None
    if strong_match and len(suggestions) > 1 and suggestions[1]['score'] == strong_match['score']:
        strong_match = None
    if strong_match:
        patient = db.session.get(Patient, strong_match['patient_id'])
        if patient and patient.status_cadastral == 'ativo':
            return patient, 'ativo_encontrado', next_code

    # 3) Buscar provisório equivalente
    existing = find_equivalent_provisional(patient_name, phone, doctor_id)
    if existing:
        return existing, 'provisorio_existente', next_code

    # 4) Criar provisório novo
    patient = Patient(
        name=patient_name,
        phone=phone or None,
        patient_type='particular',
        status_cadastral='provisorio',
    )
    db.session.add(patient)
    db.session.flush()
    db.session.add(PatientDoctor(
        patient_id=patient.id,
        doctor_id=doctor_id,
        patient_code=None,
    ))
    return patient, 'provisorio_criado', next_code


def _floor_to_slot(value):
    return value.replace(
        minute=value.minute - (value.minute % SLOT_MINUTES),
        second=0,
        microsecond=0,
    )


def _overlaps(start_time, end_time, intervals):
    return any(start_time < interval_end and end_time > interval_start
               for interval_start, interval_end in intervals)


def _assign_available_slots(rows, doctor_id):
    """Encaixa as linhas em blocos de cinco minutos sem sobreposição."""
    if not rows:
        return

    first_date = min(row['start_time'].date() for row in rows)
    last_date = max(row['start_time'].date() for row in rows)
    window_start = datetime.combine(first_date, datetime.min.time())
    window_end = datetime.combine(last_date + timedelta(days=1), datetime.min.time())
    existing = Appointment.query.filter(
        Appointment.doctor_id == doctor_id,
        Appointment.start_time < window_end,
        Appointment.end_time > window_start,
    ).all()
    intervals = [
        (appointment.start_time, appointment.end_time)
        for appointment in existing
        if normalize_appointment_status(appointment.status) != AppointmentStatus.CANCELLED
    ]

    ordered_rows = sorted(rows, key=lambda row: (row['start_time'], row['row_index']))
    for row in ordered_rows:
        requested_start = row['start_time']
        candidate_start = _floor_to_slot(requested_start)
        duration = timedelta(minutes=row['duration_minutes'])
        candidate_end = candidate_start + duration

        while _overlaps(candidate_start, candidate_end, intervals):
            candidate_start += timedelta(minutes=SLOT_MINUTES)
            candidate_end = candidate_start + duration
            if candidate_start.date() != requested_start.date():
                raise PhysicalAgendaImportError(
                    f'Linha {row["row_index"] + 1}: Não há horário livre neste dia.'
                )

        row['requested_start_time'] = requested_start
        row['start_time'] = candidate_start
        row['end_time'] = candidate_end
        row['time_adjusted'] = candidate_start != requested_start
        intervals.append((candidate_start, candidate_end))


def build_import_preview(items, doctor_id):
    """Valida e calcula os encaixes sem alterar o banco."""
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

    patient_ids = {row['patient_id'] for row in parsed_rows if row.get('patient_id')}
    patients = Patient.query.filter(Patient.id.in_(patient_ids)).all() if patient_ids else []
    patients_by_id = {patient.id: patient for patient in patients}
    links = PatientDoctor.query.filter(
        PatientDoctor.patient_id.in_(patient_ids),
        PatientDoctor.doctor_id == doctor_id,
    ).all() if patient_ids else []
    linked_patient_ids = {link.patient_id for link in links}

    for row in parsed_rows:
        if not row.get('patient_id'):
            continue
        patient = patients_by_id.get(row['patient_id'])
        if not patient:
            row['issues'].append('Paciente selecionado não encontrado.')
            continue
        if patient.status_cadastral not in {'ativo', 'provisorio'}:
            row['issues'].append('Situação cadastral do paciente não permite agendamento.')
        if patient.status_cadastral == 'provisorio' and patient.id not in linked_patient_ids:
            row['issues'].append('Paciente provisório não pertence ao médico selecionado.')
        row['patient_name'] = patient.name
        row['patient_status'] = patient.status_cadastral

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

    _assign_available_slots(parsed_rows, doctor_id)

    response_rows = []
    for row in rows:
        conflicts = row.get('conflicts', [])
        issues = list(dict.fromkeys(row.get('issues', [])))
        if conflicts:
            issues.append('Horário sobreposto a um agendamento existente.')
        response_rows.append({
            'row_index': row['row_index'],
            'ready': not issues,
            'patient_id': row.get('patient_id'),
            'patient_name': row.get('patient_name'),
            'patient_status': row.get('patient_status'),
            'start': row.get('start_time').isoformat(timespec='minutes') if row.get('start_time') else None,
            'end': row.get('end_time').isoformat(timespec='minutes') if row.get('end_time') else None,
            'requested_start': row.get('requested_start_time').isoformat(timespec='minutes') if row.get('requested_start_time') else None,
            'time_adjusted': bool(row.get('time_adjusted')),
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
    """Importa agendamentos criando pacientes provisórios automaticamente quando necessário."""
    ensure_physical_agenda_import_schema()
    if not isinstance(items, list) or not items:
        raise PhysicalAgendaImportError('Selecione ao menos uma linha para importar.')
    if len(items) > MAX_IMPORT_ITEMS:
        raise PhysicalAgendaImportError(f'O lote aceita até {MAX_IMPORT_ITEMS} linhas.')

    if db.engine.dialect.name == 'postgresql':
        db.session.execute(db.text('LOCK TABLE appointment IN SHARE ROW EXCLUSIVE MODE'))

    # 1) Parsear todos os itens
    rows = []
    for index, item in enumerate(items):
        try:
            rows.append(_parse_item(item, index))
        except PhysicalAgendaImportError as exc:
            raise PhysicalAgendaImportError(f'Linha {index + 1}: {exc}') from exc

    # 2) Resolver pacientes (ativo, provisório existente, ou criar provisório)
    next_code = None
    for row in rows:
        patient, resolution, next_code = _resolve_or_create_patient(
            row, doctor_id, next_code
        )
        if patient is None:
            raise PhysicalAgendaImportError(
                f'Linha {row["row_index"] + 1}: Não foi possível resolver o paciente.'
            )
        row['patient'] = patient
        row['patient_id'] = patient.id
        row['resolution'] = resolution

    # 3) Verificar idempotência
    keys = [row['idempotency_key'] for row in rows]
    existing_logs = {
        log.idempotency_key: log
        for log in PhysicalAgendaImportLog.query.filter(
            PhysicalAgendaImportLog.idempotency_key.in_(keys)
        ).all()
    }
    for row in rows:
        if row['idempotency_key'] in existing_logs:
            raise PhysicalAgendaImportError(
                f'Linha {row["row_index"] + 1}: Esta linha já foi importada.'
            )

    # 4) Encaixar conflitos e duplicidades no próximo bloco livre de cinco minutos
    _assign_available_slots(rows, doctor_id)

    # 6) Criar vínculos para pacientes ativos sem vínculo, e agendamentos
    linked_patient_ids = {
        link.patient_id for link in PatientDoctor.query.filter(
            PatientDoctor.doctor_id == doctor_id
        ).all()
    }

    created = []
    for row in rows:
        patient = row['patient']

        if patient.status_cadastral == 'ativo' and patient.id not in linked_patient_ids:
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
            'requested_start': row['requested_start_time'].isoformat(timespec='minutes'),
            'time_adjusted': row['time_adjusted'],
            'patient_resolution': row['resolution'],
        })

    db.session.commit()
    return created
