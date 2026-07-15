"""Tabela de preços de consulta por tipo.
Fonte única — importada pelo app.py e pelos blueprints de checkout."""

# Tipos de consulta e seus valores - determina se cobra ou não
CONSULTATION_PRICES = {
    'Particular': 400.0,           # Cobra R$400
    'Transplante Capilar': 400.0,  # Cobra R$400
    'Implante Capilar': 400.0,     # Implante Capilar cobra R$400
    '1\u00ba Implante Capilar': 400.0,  # Primeira consulta implante cobra R$400
    'Retorno': 0.0,                # Não cobra
    'Retorno Implante Capilar': 0.0,  # Retorno implante não cobra
    'UT Implante Capilar': 0.0,    # UT + Implante não cobra (retorno)
    'UNIMED': 0.0,                 # Não cobra
    'Cortesia': 0.0,               # Não cobra
    'Consulta Cortesia': 0.0       # Não cobra
}
