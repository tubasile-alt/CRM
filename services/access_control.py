"""Regras puras e reutilizáveis de autorização.

Este módulo não depende de Flask nem do banco de dados. Isso permite validar as
regras com objetos em memória e evita que rotas diferentes interpretem papéis
de formas incompatíveis.
"""


def _normalized_role(value):
    return str(value or '').strip().upper()


def is_admin_user(user):
    """Reconhece o papel administrativo nos dois campos legados de usuário."""
    return (
        _normalized_role(getattr(user, 'role', None)) == 'ADMIN'
        or _normalized_role(getattr(user, 'role_clinico', None)) == 'ADMIN'
    )


def can_manage_owned_record(user, owner_id):
    """Permite ao proprietário ou a um administrador gerenciar o registro."""
    if user is None or not getattr(user, 'is_authenticated', True):
        return False

    return getattr(user, 'id', None) == owner_id or is_admin_user(user)
