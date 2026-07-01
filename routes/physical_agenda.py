"""Etapa 1 da importação assistida de agenda física: análise sem persistência."""
import logging
import warnings
from datetime import datetime
from io import BytesIO

from flask import Blueprint, abort, current_app, jsonify, render_template, request
from flask_login import current_user, login_required
from PIL import Image, UnidentifiedImageError

from models import User
from services.clinic_time import clinic_today
from services.physical_agenda_ai import PhysicalAgendaAIError, analyze_physical_agenda_image


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
