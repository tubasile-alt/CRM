"""Matching determinístico de linhas transcritas com pacientes ativos."""
import re
import unicodedata
from difflib import SequenceMatcher

from models import Patient, PatientDoctor, db


def normalize_name(value):
    text = unicodedata.normalize('NFKD', str(value or ''))
    text = ''.join(character for character in text if not unicodedata.combining(character))
    return ' '.join(re.sub(r'[^a-zA-Z0-9 ]', ' ', text).lower().split())


def normalize_phone(value):
    return re.sub(r'\D', '', str(value or ''))[:15]


def normalize_cpf(value):
    return re.sub(r'\D', '', str(value or ''))[:11]


def _digits_expression(column):
    expression = db.func.coalesce(column, '')
    for character in ['(', ')', '-', '.', '/', ' ', '+']:
        expression = db.func.replace(expression, character, '')
    return expression


def _candidate_patients(patient_name, phone, cpf=None, patient_code=None, doctor_id=None):
    normalized_name = normalize_name(patient_name)
    phone_digits = normalize_phone(phone)
    cpf_digits = normalize_cpf(cpf)
    filters = []

    name_tokens = [token for token in normalized_name.split() if len(token) >= 2]
    if name_tokens:
        filters.extend(Patient.name.ilike(f'%{token}%') for token in name_tokens[:2])
        filters.append(Patient.name.ilike(f'%{name_tokens[0][:3]}%'))
    if len(phone_digits) >= 8:
        filters.append(_digits_expression(Patient.phone).ilike(f'%{phone_digits[-8:]}'))
    if len(cpf_digits) == 11:
        filters.append(_digits_expression(Patient.cpf) == cpf_digits)

    code_patient_ids = []
    try:
        normalized_code = int(patient_code) if str(patient_code or '').strip() else None
    except (TypeError, ValueError):
        normalized_code = None
    if normalized_code is not None and doctor_id:
        code_patient_ids = [
            link.patient_id for link in PatientDoctor.query.filter_by(
                doctor_id=doctor_id,
                patient_code=normalized_code,
            ).all()
        ]
        if code_patient_ids:
            filters.append(Patient.id.in_(code_patient_ids))

    if not filters:
        return []
    return Patient.query.filter(
        Patient.status_cadastral == 'ativo',
        db.or_(*filters),
    ).limit(50).all()


def suggest_active_patients(patient_name, phone, doctor_id, cpf=None, patient_code=None, limit=3):
    """Retorna sugestões ativas sem alterar vínculos ou cadastros."""
    normalized_name = normalize_name(patient_name)
    phone_digits = normalize_phone(phone)
    cpf_digits = normalize_cpf(cpf)
    try:
        normalized_code = int(patient_code) if str(patient_code or '').strip() else None
    except (TypeError, ValueError):
        normalized_code = None
    candidates = _candidate_patients(patient_name, phone, cpf, normalized_code, doctor_id)
    if not candidates:
        return []

    patient_ids = [patient.id for patient in candidates]
    links = PatientDoctor.query.filter(
        PatientDoctor.patient_id.in_(patient_ids),
        PatientDoctor.doctor_id == doctor_id,
    ).all()
    links_by_patient = {link.patient_id: link for link in links}

    suggestions = []
    for patient in candidates:
        candidate_name = normalize_name(patient.name)
        candidate_phone = normalize_phone(patient.phone)
        candidate_cpf = normalize_cpf(patient.cpf)
        name_ratio = SequenceMatcher(None, normalized_name, candidate_name).ratio() if normalized_name else 0
        score = 0.0
        reasons = []

        if phone_digits and candidate_phone == phone_digits:
            score = 1.0
            reasons.append('telefone exato')
        elif len(phone_digits) >= 8 and candidate_phone.endswith(phone_digits[-8:]):
            score = 0.97
            reasons.append('telefone compatível')

        link = links_by_patient.get(patient.id)
        if len(cpf_digits) == 11 and candidate_cpf == cpf_digits:
            score = 1.0
            reasons.append('CPF exato')
        if normalized_code is not None and link and link.patient_code == normalized_code:
            score = 1.0
            reasons.append('código exato')

        if normalized_name and candidate_name == normalized_name:
            score = max(score, 0.95)
            reasons.append('nome exato')
        elif name_ratio >= 0.72:
            score = max(score, round(name_ratio * 0.9, 2))
            reasons.append('nome semelhante')

        if link and score:
            score = min(1.0, score + 0.01)
        if score < 0.65:
            continue

        suggestions.append({
            'patient_id': patient.id,
            'patient_name': patient.name,
            'patient_phone': patient.phone or '',
            'patient_cpf_suffix': candidate_cpf[-2:] if candidate_cpf else '',
            'patient_code': link.patient_code if link else None,
            'linked_to_doctor': bool(link),
            'score': round(score, 2),
            'reason': ', '.join(dict.fromkeys(reasons)),
        })

    suggestions.sort(key=lambda item: (-item['score'], not item['linked_to_doctor'], item['patient_name']))
    return suggestions[:limit]


def find_equivalent_provisional(patient_name, phone, doctor_id):
    """Evita criar duplicata provisória para o mesmo médico."""
    normalized_name = normalize_name(patient_name)
    phone_digits = normalize_phone(phone)
    query = Patient.query.join(PatientDoctor).filter(
        Patient.status_cadastral == 'provisorio',
        PatientDoctor.doctor_id == doctor_id,
    )

    for patient in query.limit(100).all():
        same_name = normalized_name and normalize_name(patient.name) == normalized_name
        same_phone = phone_digits and normalize_phone(patient.phone) == phone_digits
        if same_name or same_phone:
            return patient
    return None
