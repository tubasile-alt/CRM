"""Contrato único dos estados de um dispatch de mensagem.

O fluxo de dispatch cria registros como ``pendente`` ou ``pulada``, pode
reservá-los como ``reservada`` e recebe do integrador um resultado terminal:
``enviada``, ``falhou`` ou ``cancelada``. A reconciliação da aba Botox aceita
todos esses estados conhecidos. Valores fora deste contrato são dados
inesperados e devem ser exibidos como ``desconhecido``, nunca como um estado
arbitrário da planilha.
"""

DISPATCH_PENDING_STATUS = 'pendente'
DISPATCH_SKIPPED_STATUS = 'pulada'
DISPATCH_CREATED_STATUSES = frozenset({
    DISPATCH_PENDING_STATUS,
    DISPATCH_SKIPPED_STATUS,
})
DISPATCH_RESERVED_STATUS = 'reservada'
DISPATCH_RESULT_STATUSES = frozenset({'enviada', 'falhou', 'cancelada'})
DISPATCH_KNOWN_STATUSES = frozenset({
    *DISPATCH_CREATED_STATUSES,
    DISPATCH_RESERVED_STATUS,
    *DISPATCH_RESULT_STATUSES,
})
DISPATCH_ACTIVE_STATUSES = frozenset({
    DISPATCH_PENDING_STATUS,
    DISPATCH_RESERVED_STATUS,
})
UNKNOWN_DISPATCH_STATUS = 'desconhecido'