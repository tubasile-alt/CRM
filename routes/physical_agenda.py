"""Etapa 1 da importação assistida de agenda física: análise sem persistência."""
import logging
import warnings
from datetime import datetime
from io import BytesIO

from flask import Blueprint, abort, current_app, jsonify, render_template, request
from flask_login import current_user, login_required
from PIL import Image, UnidentifiedImageError

from models import Patient, PatientDoctor, User, db
from services.clinic_time import clinic_today
from services.physical_agenda_ai import PhysicalAgendaAIError, analyze_physical_agenda_image
from services.physical_agenda_import import (
    PhysicalAgendaImportError,
    build_import_preview,
    import_appointments,
)
from services.physical_agenda_matching import (
    find_equivalent_provisional,
    normalize_phone,
    suggest_active_patients,
)


physical_agenda_bp = Blueprint('physical_agenda', __name__)
logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp'}
ALLOWED_FORMATS = {
    'JPEG': 'image/jpeg',
    'PNG': 'image/png',
    'WEBP': 'image/webp',
}


def _can_use_importer(user):
    return user.is_doctor() or user.is_secretary() or user.is_admin()


def _available_doctors():
    if current_user.is_doctor() and not current_user.is_admin():
        return [current_user]
    return User.query.filter_by(role='medico').order_by(User.name).all()


def _error(message, status=400):
    response = jsonify({'success': False, 'error': message})
    response.headers['Cache-Control'] = 'no-store'
    return response, status


def _error_with_data(message, status, **data):
    payload = {'success': False, 'error': message}
    payload.update(data)
    response = jsonify(payload)
    response.headers['Cache-Control'] = 'no-store'
    return response, status


def _validated_doctor(doctor_id):
    doctor = User.query.filter_by(id=doctor_id, role='medico').first()
    if not doctor:
        return None, _error('Médico responsável inválido.')
    if current_user.is_doctor() and not current_user.is_admin() and doctor.id != current_user.id:
        return None, _error('Médicos só podem analisar a própria agenda.', 403)
    return doctor, None


def _upload_limit():
    max_mb = max(1, int(current_app.config.get('PHYSICAL_AGENDA_UPLOAD_MAX_MB', 10)))
    return max_mb, max_mb * 1024 * 1024


def _read_validated_image(upload):
    filename = (upload.filename or '').strip()
    extension = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    if extension not in ALLOWED_EXTENSIONS:
        raise ValueError('Formato inválido. Envie uma imagem JPG, PNG ou WEBP.')

    max_mb, max_bytes = _upload_limit()
    image_bytes = upload.stream.read(max_bytes + 1)
    if not image_bytes:
        raise ValueError('A imagem enviada está vazia.')
    if len(image_bytes) > max_bytes:
        raise ValueError(f'A imagem excede o limite de {max_mb} MB.')

    try:
        with warnings.catch_warnings():
            warnings.simplefilter('error', Image.DecompressionBombWarning)
            with Image.open(BytesIO(image_bytes)) as image:
                image_format = image.format
                image.verify()
    except (UnidentifiedImageError, OSError, Image.DecompressionBombWarning) as exc:
        raise ValueError('O arquivo enviado não é uma imagem válida.') from exc

    mime_type = ALLOWED_FORMATS.get(image_format)
    if not mime_type:
        raise ValueError('Formato inválido. Envie uma imagem JPG, PNG ou WEBP.')
    return image_bytes, mime_type


@physical_agenda_bp.route('/agenda/importar-fisica', methods=['GET'])
@login_required
def import_page():
    if not _can_use_importer(current_user):
        abort(403)

    doctors = _available_doctors()
    selected_doctor_id = current_user.id if current_user.is_doctor() and not current_user.is_admin() else None
    return render_template(
        'physical_agenda_import.html',
        doctors=doctors,
        selected_doctor_id=selected_doctor_id,
        agenda_date=clinic_today().isoformat(),
        max_upload_mb=current_app.config.get('PHYSICAL_AGENDA_UPLOAD_MAX_MB', 10),
    )


@physical_agenda_bp.route('/api/agenda-fisica/analisar', methods=['POST'])
@login_required
def analyze():
    if not _can_use_importer(current_user):
        return _error('Você não tem permissão para analisar agendas físicas.', 403)

    max_mb, max_bytes = _upload_limit()
    if request.content_length and request.content_length > max_bytes + (1024 * 1024):
        return _error(f'A imagem excede o limite de {max_mb} MB.', 413)

    agenda_date_raw = (request.form.get('date') or '').strip()
    try:
        agenda_date = datetime.strptime(agenda_date_raw, '%Y-%m-%d').date()
    except ValueError:
        return _error('Informe uma data válida para a agenda.')

    try:
        doctor_id = int(request.form.get('doctor_id') or '')
    except (TypeError, ValueError):
        return _error('Selecione o médico responsável.')

    doctor, doctor_error = _validated_doctor(doctor_id)
    if doctor_error:
        return doctor_error

    upload = request.files.get('image')
    if not upload or not upload.filename:
        return _error('Selecione uma imagem da agenda física.')

    try:
        image_bytes, mime_type = _read_validated_image(upload)
    except ValueError as exc:
        return _error(str(exc))

    if not current_app.config.get('OPENAI_API_KEY'):
        return _error('OPENAI_API_KEY não configurada. Contate o administrador.', 503)

    try:
        result = analyze_physical_agenda_image(
            image_bytes=image_bytes,
            mime_type=mime_type,
            agenda_date=agenda_date.isoformat(),
            doctor_name=doctor.name,
        )
    except PhysicalAgendaAIError as exc:
        return _error(str(exc), 502)
    except Exception:
        logger.exception('Falha não identificada no endpoint de análise de agenda física.')
        return _error('Não foi possível analisar a imagem. Tente novamente.', 500)

    response = jsonify({
        'success': True,
        'agenda_date': agenda_date.isoformat(),
        'doctor_id': doctor.id,
        'doctor_name': doctor.name,
        'items': result['items'],
        'warnings': result['warnings'],
    })
    response.headers['Cache-Control'] = 'no-store'
    return response


@physical_agenda_bp.route('/api/agenda-fisica/sugerir-pacientes', methods=['POST'])
@login_required
def suggest_patients():
    if not _can_use_importer(current_user):
        return _error('Você não tem permissão para pesquisar pacientes.', 403)

    data = request.get_json(silent=True) or {}
    try:
        doctor_id = int(data.get('doctor_id') or '')
    except (TypeError, ValueError):
        return _error('Selecione o médico responsável.')

    _, doctor_error = _validated_doctor(doctor_id)
    if doctor_error:
        return doctor_error

    items = data.get('items')
    if not isinstance(items, list):
        return _error('Lista de pacientes inválida.')

    matches = []
    for index, item in enumerate(items[:100]):
        if not isinstance(item, dict):
            continue
        name = str(item.get('patient_name') or '').strip()[:160]
        phone = str(item.get('phone') or '').strip()[:40]
        cpf = str(item.get('cpf') or '').strip()[:20]
        patient_code = str(item.get('patient_code') or '').strip()[:20]
        phone_digits = normalize_phone(phone)
        if not patient_code and 1 <= len(phone_digits) <= 6:
            patient_code = phone_digits
            phone = ''
        matches.append({
            'row_index': index,
            'suggestions': suggest_active_patients(
                name,
                phone,
                doctor_id,
                cpf=cpf,
                patient_code=patient_code,
            ),
        })

    response = jsonify({'success': True, 'matches': matches})
    response.headers['Cache-Control'] = 'no-store'
    return response


@physical_agenda_bp.route('/api/agenda-fisica/pacientes-provisorios', methods=['POST'])
@login_required
def create_provisional_patient():
    """Cria cadastro provisório somente após ação explícita na conferência."""
    if not _can_use_importer(current_user):
        return _error('Você não tem permissão para criar cadastro provisório.', 403)

    data = request.get_json(silent=True) or {}
    try:
        doctor_id = int(data.get('doctor_id') or '')
    except (TypeError, ValueError):
        return _error('Selecione o médico responsável.')

    _, doctor_error = _validated_doctor(doctor_id)
    if doctor_error:
        return doctor_error

    patient_name = ' '.join(str(data.get('patient_name') or '').split()).strip()
    phone = normalize_phone(data.get('phone')) or None
    if not patient_name:
        return _error('Informe o nome antes de criar o cadastro provisório.')
    if len(patient_name) > 100:
        return _error('O nome do paciente excede 100 caracteres.')

    active_suggestions = suggest_active_patients(patient_name, phone, doctor_id)
    strong_matches = [suggestion for suggestion in active_suggestions if suggestion['score'] >= 0.9]
    if strong_matches:
        return _error_with_data(
            'Paciente ativo semelhante encontrado. Selecione o cadastro existente.',
            409,
            suggestions=strong_matches,
        )

    existing_provisional = find_equivalent_provisional(patient_name, phone, doctor_id)
    if existing_provisional:
        return _error_with_data(
            'Já existe um cadastro provisório equivalente para este médico.',
            409,
            existing_provisional={
                'patient_id': existing_provisional.id,
                'patient_name': existing_provisional.name,
                'patient_phone': existing_provisional.phone or '',
            },
        )

    try:
        patient = Patient(
            name=patient_name,
            phone=phone,
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
        db.session.commit()
    except Exception:
        db.session.rollback()
        logger.error('Falha técnica ao criar cadastro provisório pela agenda física.')
        return _error('Não foi possível criar o cadastro provisório.', 500)

    response = jsonify({
        'success': True,
        'patient': {
            'patient_id': patient.id,
            'patient_name': patient.name,
            'patient_phone': patient.phone or '',
            'status_cadastral': patient.status_cadastral,
        },
    })
    response.headers['Cache-Control'] = 'no-store'
    return response, 201


def _import_request_data():
    data = request.get_json(silent=True) or {}
    try:
        doctor_id = int(data.get('doctor_id') or '')
    except (TypeError, ValueError):
        return None, None, _error('Selecione o médico responsável.')

    _, doctor_error = _validated_doctor(doctor_id)
    if doctor_error:
        return None, None, doctor_error
    return data, doctor_id, None


@physical_agenda_bp.route('/api/agenda-fisica/previsualizar-importacao', methods=['POST'])
@login_required
def preview_import():
    if not _can_use_importer(current_user):
        return _error('Você não tem permissão para importar agendamentos.', 403)

    data, doctor_id, validation_error = _import_request_data()
    if validation_error:
        return validation_error

    try:
        preview = build_import_preview(data.get('items'), doctor_id)
    except PhysicalAgendaImportError as exc:
        return _error(str(exc))
    except Exception:
        logger.exception('Falha técnica na prévia da importação de agenda física.')
        return _error('Não foi possível validar os agendamentos.', 500)

    response = jsonify({
        'success': True,
        'ready': preview['ready'],
        'rows': preview['rows'],
    })
    response.headers['Cache-Control'] = 'no-store'
    return response


@physical_agenda_bp.route('/api/agenda-fisica/importar', methods=['POST'])
@login_required
def confirm_import():
    if not _can_use_importer(current_user):
        return _error('Você não tem permissão para importar agendamentos.', 403)

    data, doctor_id, validation_error = _import_request_data()
    if validation_error:
        return validation_error
    if data.get('confirmed') is not True:
        return _error('Confirme explicitamente a criação dos agendamentos.')

    try:
        created, preview = import_appointments(
            data.get('items'),
            doctor_id,
            current_user.id,
        )
        if created is None:
            db.session.rollback()
            return _error_with_data(
                'Existem pendências ou conflitos. Revise a prévia antes de importar.',
                409,
                ready=False,
                rows=preview['rows'],
            )
    except PhysicalAgendaImportError as exc:
        db.session.rollback()
        return _error(str(exc))
    except Exception:
        db.session.rollback()
        logger.exception('Falha técnica ao importar agenda física.')
        return _error('Não foi possível criar os agendamentos. Nenhuma linha foi importada.', 500)

    response = jsonify({
        'success': True,
        'created_count': len(created),
        'appointments': created,
    })
    response.headers['Cache-Control'] = 'no-store'
    return response, 201
