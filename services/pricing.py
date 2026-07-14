"""Tabela de preços de consulta por tipo.
Fonte única — importada pelo app.py e pelos blueprints de checkout."""

# Tipos de consulta e seus valores - determina se cobra ou não
CONSULTATION_PRICES = {
    'Particular': 400.0,           # Cobra R$400
    'Transplante Capilar': 400.0,  # Cobra R$400
    'Retorno': 0.0,                # Não cobra
    'UNIMED': 0.0,                 # Não cobra
    'Cortesia': 0.0,               # Não cobra
    'Consulta Cortesia': 0.0       # Não cobra
}
