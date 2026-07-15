"""Normalizacao de tipos de consulta — converte abreviacoes do provisorio para nomes oficiais."""

OFFICIAL_APPOINTMENT_TYPES = [
    'Particular', 'Patologia', 'Botox', 'Retorno Botox', 'Laser',
    'Preenchimento', 'Retorno Preenchimento', 'Sculptra', 'Ulthera',
    'Retorno Ulthera', 'Morpheus', 'Retorno Morpheus',
    'Implante Capilar', '1\u00ba Implante Capilar', 'Retorno Implante Capilar',
    'UT Implante Capilar', 'Infiltra\u00e7\u00e3o Capilar', 'Soroterapia',
    'Pequena Cirurgia', 'Retirada de Ponto', 'Nitrog\u00eanio L\u00edquido',
    'Transplante Capilar', 'Retorno 1 semana TX', 'Retorno Transplante',
    'Retorno', 'UNIMED', 'Cortesia'
]

# Mapeamento de abreviacoes → tipos oficiais (case-insensitive)
ABBREVIATION_MAP = {
    # Retornos
    'ret': 'Retorno',
    'retorno': 'Retorno',
    '1\u00ba ret': 'Retorno',
    'ret cons': 'Retorno',
    # Consulta particular
    'cons': 'Particular',
    'part.': 'Particular',
    'part': 'Particular',
    # UNIMED
    'us': 'UNIMED',
    'uti': 'UNIMED',
    'utc': 'UNIMED',
    'uds': 'UNIMED',
    'und': 'UNIMED',
    'chs': 'UNIMED',
    'vns': 'UNIMED',
    'vnd': 'UNIMED',
    'vet': 'UNIMED',
    'out': 'UNIMED',
    # IC (Implante Capilar) — seguranca extra caso ainda apareca
    'ic': 'Implante Capilar',
    '1\u00ba ic': '1\u00ba Implante Capilar',
    'ret ic': 'Retorno Implante Capilar',
    'ut ic': 'Retorno Implante Capilar',
    'ut uc': 'Retorno Implante Capilar',
}


def normalize_appointment_type(value):
    """Converte abreviacoes do provisorio para tipo oficial da lista.

    - Se ja for um tipo oficial (case-sensitive match), retorna ele mesmo.
    - Se for uma abreviacao conhecida, converte para o oficial.
    - Se nao reconhecer, retorna o valor original (nao altera tipos desconhecidos).
    """
    if not value or not isinstance(value, str):
        return 'Particular'

    value = value.strip()

    # Ja e oficial? Retorna direto
    if value in OFFICIAL_APPOINTMENT_TYPES:
        return value

    # Match case-insensitive na lista oficial
    lower = value.lower()
    for official in OFFICIAL_APPOINTMENT_TYPES:
        if official.lower() == lower:
            return official

    # Match via mapa de abreviacoes
    mapped = ABBREVIATION_MAP.get(lower)
    if mapped:
        return mapped

    # Nao reconheceu — retorna original
    return value
