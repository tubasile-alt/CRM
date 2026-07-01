"""Prévia e importação transacional de linhas da agenda física."""
from datetime import datetime, timedelta

from models import Appointment, Patient, PatientDoctor, PhysicalAgendaImportLog, db
from services.physical_agenda_matching import (
    find_equivalent_provisional,
    normalize_name,
    normalize_phone,
    suggest_active_patients,
)
from services.physical_agenda_schema_service import ensure_physical_agenda_import_schema
from services.statuses import AppointmentStatus, normalize_appointment_status


MAX_IMPORT_ITEMS = 100
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
        duration = int(item.get('duration_minutes') or 15)
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

    # 1) Paciente explicitamente selecionado pelo usuário no frontend
    explicit_patient_id = item.get('patient_id')
    if explicit_patient_id:
        patient = Patient.query.get(int(explicit_patient_id))
        if patient and patient.status_cadastral in {'ativo', 'provisorio'}:
            status = 'ativo_selecionado' if patient.status_cadastral == 'ativo' else 'provisorio_selecionado'
            return patient, status, next_code

    if not patient_name:
        return None, None, next_code

    # 2) Buscar ativo com match forte (score >= 0.9)
    suggestions = suggest_active_patients(patient_name, phone, doctor_id, limit=5)
    strong_match = next((s for s in suggestions if s['score'] >= 0.9), None)
    if strong_match:
        patient = Patient.query.get(strong_match['patient_id'])
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


def _serialize_conflict(appointment):
    return {
        'appointment_id': appointment.id,
        'start': appointment.start_time.isoformat(timespec='minutes'),
        'end': appointment.end_time.isoformat(timespec='minutes'),
        'patient_name': appointment.patient.name if appointment.patient else 'Paciente',
        'status': normalize_appointment_status(appointment.status),
    }


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
        window_start = min(row['start_time'] for row in parsed_rows)
        window_end = max(row['end_time'] for row in parsed_rows)
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

        for appointment in existing_appointments:
            if appointment.start_time < row['end_time'] and appointment.end_time > row['start_time']:
                row['conflicts'].append(_serialize_conflict(appointment))

    for index, left in enumerate(parsed_rows):
        for right in parsed_rows[index + 1:]:
            if left['start_time'] < right['end_time'] and left['end_time'] > right['start_time']:
                left['issues'].append(f'Conflito com a linha {right["row_index"] + 1} do lote.')
                right['issues'].append(f'Conflito com a linha {left["row_index"] + 1} do lote.')

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

    # 4) Verificar conflitos de horário com agendamentos existentes
    if rows:
        window_start = min(row['start_time'] for row in rows)
        window_end = max(row['end_time'] for row in rows)
        existing = Appointment.query.filter(
            Appointment.doctor_id == doctor_id,
            Appointment.start_time < window_end,
            Appointment.end_time > window_start,
        ).all()
        existing = [
            a for a in existing
            if normalize_appointment_status(a.status) != AppointmentStatus.CANCELLED
        ]
        for row in rows:
            for apt in existing:
                if apt.start_time < row['end_time'] and apt.end_time > row['start_time']:
                    pname = apt.patient.name if apt.patient else 'Paciente'
                    raise PhysicalAgendaImportError(
                        f'Linha {row["row_index"] + 1}: Conflito com agendamento existente '
                        f'({pname} {apt.start_time.strftime("%H:%M")}-{apt.end_time.strftime("%H:%M")}).'
                    )

    # 5) Verificar conflitos internos
    for i, left in enumerate(rows):
        for right in rows[i + 1:]:
            if left['start_time'] < right['end_time'] and left['end_time'] > right['start_time']:
                raise PhysicalAgendaImportError(
                    f'Linha {left["row_index"] + 1}: Conflito com linha {right["row_index"] + 1}.'
                )

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
            'patient_resolution': row['resolution'],
        })

    db.session.commit()
    return created
