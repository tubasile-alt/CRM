from flask import abort
from flask_login import current_user
from models import db, PatientDoctor


def _get_dp(dp_id):
    return PatientDoctor.query.get_or_404(dp_id)


def can_view_dp(dp):
    if not current_user.is_authenticated:
        return False
    # Secretárias e Admins podem ver tudo
    if current_user.role_clinico in ('SECRETARY', 'ADMIN') or current_user.is_secretary():
        return True
    return dp.doctor_id == current_user.id


def can_edit_dp(dp):
    if not current_user.is_authenticated:
        return False
    # Secretárias e Admins podem editar (necessário para salvar triagem/dados iniciais)
    if current_user.role_clinico in ('SECRETARY', 'ADMIN') or current_user.is_secretary():
        return True
    return dp.doctor_id == current_user.id


def require_dp_view(dp_id):
    dp = _get_dp(dp_id)
    if not can_view_dp(dp):
        abort(403)
    return dp


def require_dp_edit(dp_id):
    dp = _get_dp(dp_id)
    if not can_edit_dp(dp):
        abort(403)
    return dp
