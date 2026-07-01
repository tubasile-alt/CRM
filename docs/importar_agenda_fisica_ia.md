# Importar Agenda Física por IA - Etapas 1 e 2

## Objetivo

A etapa 1 transcreve uma ou mais imagens JPG, PNG ou WEBP de páginas da agenda física e apresenta os compromissos em uma tabela editável para conferência. Cada foto recebe sua própria data e pode representar um dia diferente.

A análise não cria pacientes, não cria agendamentos e não altera registros existentes. A imagem não é persistida pelo CRM. A requisição à Responses API usa `store=False`.

Depois da conferência, o usuário pode pesquisar correspondências entre as linhas transcritas e pacientes ativos. Quando não houver correspondência, uma ação manual e confirmada pode criar somente um cadastro provisório, sem prontuário ou código.

A etapa 2 permite pré-visualizar conflitos e criar os agendamentos selecionados. A gravação só ocorre depois de uma segunda confirmação explícita e o lote inteiro é transacional: se uma linha falhar, nenhuma é criada.

## Configuração

Configure as variáveis como secrets do ambiente de execução:

```text
OPENAI_API_KEY=...
OPENAI_VISION_MODEL=gpt-4.1-mini
PHYSICAL_AGENDA_UPLOAD_MAX_MB=10
```

- `OPENAI_API_KEY` é obrigatória e não deve ser adicionada ao repositório.
- `OPENAI_VISION_MODEL` aceita um modelo multimodal compatível com Responses API e Structured Outputs.
- `PHYSICAL_AGENDA_UPLOAD_MAX_MB` é opcional e usa 10 MB por padrão.

O projeto requer `openai>=2.0.0,<3.0.0`. Depois de atualizar o código no Replit, execute a instalação de `requirements.txt` antes de iniciar a aplicação.

## Fluxo de uso

1. A secretária abre **Importar Agenda Física** no menu principal.
2. Seleciona a data e o médico responsável.
3. Fotografa, escolhe ou arrasta uma ou mais imagens das páginas da agenda.
4. Confere ou altera a data individual de cada foto adicionada.
5. Seleciona **Analisar agenda**. As fotos são processadas uma por vez e reunidas na mesma conferência.
6. Confere e corrige data, horário, nome, telefone, tipo, procedimento e observações.
7. Confere as sugestões de pacientes ativos por nome, telefone, CPF ou código.
8. Quando nenhum paciente corresponder, pode confirmar a criação de um cadastro provisório.
9. Ajusta a duração e desmarca linhas que não devem entrar na agenda.
10. Seleciona **Pré-visualizar importação** e corrige eventuais conflitos.
11. Quando todas as linhas estiverem prontas, seleciona **Criar agendamentos** e confirma a operação.
12. Também pode copiar ou baixar o JSON revisado, agrupado por data.

Médicos só podem analisar a própria agenda. Secretária e administrador podem selecionar qualquer usuário cadastrado como médico.

## Segurança e privacidade

- A imagem não é gravada em disco nem no banco.
- O lote permanece apenas na memória da página enquanto ela estiver aberta.
- O endpoint de análise não executa `INSERT`, `UPDATE` ou `DELETE`.
- A criação provisória existe em endpoint separado, exige ação explícita e não cria agendamento.
- A criação de agendamentos exige prévia válida e confirmação explícita.
- A confirmação recalcula conflitos dentro de uma transação antes de gravar.
- Cada agendamento importado recebe uma chave idempotente e um registro técnico de auditoria.
- Nomes, telefones, imagem e resposta da IA não são registrados em logs.
- Arquivos são limitados por tamanho, extensão e formato real da imagem.
- A interface aceita até 10 fotos por lote para limitar consumo de memória e chamadas acidentais.
- A chave da OpenAI é lida apenas de variável de ambiente.
- A imagem contém dados pessoais e é enviada à API da OpenAI para transcrição; o uso deve seguir as políticas internas de privacidade da clínica.

## Limitações

- Manuscritos pouco legíveis podem gerar campos nulos ou baixa confiança.
- O matching é determinístico por nome, telefone, CPF e código e sempre exige conferência humana.
- O telefone normalizado deve ser conferido contra o texto da agenda.
- O checkbox **Importar?** controla tanto o JSON quanto as linhas enviadas para a agenda.
- Não existe persistência do resultado depois que a página é fechada.
- Conflitos de horário bloqueiam a importação e não podem ser forçados nesta fase.
- A importação cria `Appointment`; integrações específicas de cirurgia, Google Sheets e Google Calendar continuam no fluxo manual da agenda.

## Banco de dados

A etapa 2 adiciona a tabela `physical_agenda_import_log` pela migration:

```text
e2f3a4b5c6d7_create_physical_agenda_import_log.py
```

Como compatibilidade com deploys que não executam Alembic automaticamente, a tabela também é criada com `checkfirst=True` no primeiro uso. Nenhuma imagem ou transcrição é armazenada nessa tabela; apenas IDs técnicos, data de origem, usuário responsável e chave de idempotência.
