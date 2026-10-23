# Agenda timeline design QA

## Objetivo

Manter a régua vertical de horários como referência prática para agendamento e alinhar cada cartão ao horário real do atendimento.

## Verificações visuais

- A régua e os cartões compartilham a mesma rolagem vertical.
- Cada cartão começa na posição correspondente ao seu horário de início.
- Atendimentos simultâneos ocupam colunas lado a lado, sem sobreposição.
- A régua permanece em intervalos de 15 minutos e continua acionável para iniciar um agendamento naquele horário.
- A grade segue até o fim do expediente e se expande para atendimentos fora do intervalo padrão.
- O estado vazio mantém a régua visível.

## Validação

- Prévia local da agenda conferida visualmente no Chrome com horários e atendimentos de demonstração.
- `tests/test_agenda_timeline.py`: 3 testes aprovados.
- `node --check static/js/agenda.js` e `git diff --check`: aprovados.
- A suíte geral não completou a coleta: dois testes importam o WeasyPrint, cuja dependência nativa `gobject-2.0-0` não está instalada neste ambiente.

## Limitação conhecida

Cartões simultâneos ficam em faixas lado a lado; em faixas estreitas, rótulos auxiliares e texto dos botões são ocultados para preservar os controles e evitar colisões.
