import base64
import binascii
from io import BytesIO

from PIL import Image, ImageOps, UnidentifiedImageError

from models import PatientPhoto, db


MAX_SOURCE_SIZE = 5 * 1024 * 1024
PHOTO_SIZE = (300, 400)
PHOTO_MIME_TYPE = 'image/jpeg'


def _normalize_image(source_bytes):
    if not source_bytes:
        raise ValueError('A foto está vazia.')
    if len(source_bytes) > MAX_SOURCE_SIZE:
        raise ValueError('Arquivo muito grande. Máximo 5MB.')

    try:
        with Image.open(BytesIO(source_bytes)) as source:
            source.load()
            image = ImageOps.exif_transpose(source)
            if image.mode != 'RGB':
                image = image.convert('RGB')
            image.thumbnail(PHOTO_SIZE, Image.Resampling.LANCZOS)

            output = BytesIO()
            image.save(output, 'JPEG', quality=70, optimize=True)
            return output.getvalue()
    except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError) as exc:
        raise ValueError('O arquivo enviado não é uma imagem válida.') from exc


def decode_photo_data_url(photo_data):
    if not photo_data or not photo_data.startswith('data:image/'):
        raise ValueError('Formato da foto inválido.')

    try:
        _, encoded = photo_data.split(',', 1)
        return base64.b64decode(encoded, validate=True)
    except (ValueError, binascii.Error) as exc:
        raise ValueError('Os dados da foto estão corrompidos.') from exc


def save_patient_photo(patient, source_bytes):
    photo_bytes = _normalize_image(source_bytes)
    photo = patient.photo_file
    if photo is None:
        photo = PatientPhoto(patient=patient)
        db.session.add(photo)

    photo.data = photo_bytes
    photo.mime_type = PHOTO_MIME_TYPE
    patient.photo_url = f'/api/patient/{patient.id}/photo/file'
    return patient.photo_url


def save_patient_photo_data_url(patient, photo_data):
    return save_patient_photo(patient, decode_photo_data_url(photo_data))


def delete_patient_photo(patient):
    if patient.photo_file is not None:
        db.session.delete(patient.photo_file)
    patient.photo_url = None
