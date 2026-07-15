"""Tabela de preços de consulta por tipo.
Fonte única — importada pelo app.py e pelos blueprints de checkout."""

# Tipos de consulta e seus valores - determina se cobra ou não
CONSULTATION_PRICES = {
    'Particular': 400.0,           # Cobra R$400
    'Transplante Capilar': 400.0,  # Cobra R$400
    'IC': 400.0,                   # Infiltração Capilar cobra R$400
    '1\u00ba IC': 400.0,           # Primeira IC cobra R$400
    'Retorno': 0.0,                # Não cobra
    'ret IC': 0.0,                 # Retorno IC não cobra
    'ut IC': 0.0,                  # Ultrassom + IC não cobra (retorno)
    'UNIMED': 0.0,                 # Não cobra
    'Cortesia': 0.0,               # Não cobra
    'Consulta Cortesia': 0.0       # Não cobra
}
