"""Shared helpers extracted from app.py without behavior changes."""

from flask_login import current_user
from models import User


def get_doctor_id():
    """Retorna o ID do médico - se o usuário atual é médico, retorna seu ID"""
    if current_user.is_doctor():
        return current_user.id
    else:
        # Secretária: retorna None para permitir seleção de médico no frontend
        return None

def get_all_doctors():
    """Retorna todos os médicos com suas preferências de cor"""
    from models import DoctorPreference
    doctors = User.query.filter_by(role='medico').all()
    result = []
    for doctor in doctors:
        pref = DoctorPreference.query.filter_by(user_id=doctor.id).first()
        result.append({
            'id': doctor.id,
            'name': doctor.name,
            'color': pref.color if pref else '#0d6efd',
            'layer_enabled': pref.layer_enabled if pref else True
        })
    return result
