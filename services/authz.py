from flask import abort
from flask_login import current_user
from models import db, PatientDoctor


def _get_dp(dp_id):
    return PatientDoctor.query.get_or_404(dp_id)


def can_view_dp(dp):
    if not current_user.is_authenticated:
        return False
    
    # Verificação de papel (role)
    user_role = getattr(current_user, 'role', '').upper()
    user_role_clinico = getattr(current_user, 'role_clinico', '').upper()
    
    # Secretárias e Admins podem ver tudo
    is_sec = (
        user_role == 'SECRETARY' or 
        user_role_clinico == 'SECRETARY' or
        getattr(current_user, 'username', '') in ('erica', 'gisele', 'recepcao') or
        (hasattr(current_user, 'is_secretary') and current_user.is_secretary())
    )
    
    if is_sec or user_role == 'ADMIN' or user_role_clinico == 'ADMIN':
        return True
        
    return dp.doctor_id == current_user.id


def can_edit_dp(dp):
    if not current_user.is_authenticated:
        return False
        
    user_role = getattr(current_user, 'role', '').upper()
    user_role_clinico = getattr(current_user, 'role_clinico', '').upper()
    
    # Secretárias podem visualizar, mas não podem editar conteúdo clínico.
    # Edição fica restrita a médico responsável ou admin.
    is_sec = (
        user_role == 'SECRETARY' or 
        user_role_clinico == 'SECRETARY' or
        getattr(current_user, 'username', '') in ('erica', 'gisele', 'recepcao') or
        (hasattr(current_user, 'is_secretary') and current_user.is_secretary())
    )
    
    if is_sec:
        return False

    if user_role == 'ADMIN' or user_role_clinico == 'ADMIN':
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
