# Importar Agenda Física por IA - Etapa 1

## Objetivo

A etapa 1 transcreve uma imagem JPG, PNG ou WEBP de uma página da agenda física e apresenta os compromissos em uma tabela editável para conferência.

Ela não cria pacientes, não cria agendamentos e não altera registros existentes. A imagem é processada em memória e não é salva pelo CRM. A requisição à Responses API usa `store=False`.

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
3. Fotografa ou escolhe uma imagem da página da agenda.
4. Seleciona **Analisar agenda**.
5. Confere e corrige horário, nome, telefone, tipo, procedimento e observações.
6. Desmarca linhas que não devem entrar no JSON de conferência.
7. Copia ou baixa o JSON revisado.

Médicos só podem analisar a própria agenda. Secretária e administrador podem selecionar qualquer usuário cadastrado como médico.

## Segurança e privacidade

- A imagem não é gravada em disco nem no banco.
- O endpoint não executa `INSERT`, `UPDATE` ou `DELETE`.
- Nomes, telefones, imagem e resposta da IA não são registrados em logs.
- Arquivos são limitados por tamanho, extensão e formato real da imagem.
- A chave da OpenAI é lida apenas de variável de ambiente.
- A imagem contém dados pessoais e é enviada à API da OpenAI para transcrição; o uso deve seguir as políticas internas de privacidade da clínica.

## Limitações

- Manuscritos pouco legíveis podem gerar campos nulos ou baixa confiança.
- A IA não confirma se o paciente já existe no CRM.
- O telefone normalizado deve ser conferido contra o texto da agenda.
- O checkbox **Importar?** controla apenas o JSON exportado nesta etapa.
- Não existe persistência do resultado depois que a página é fechada.

## Etapa 2

A próxima etapa poderá adicionar, sempre após confirmação explícita:

- matching com pacientes existentes por nome, telefone, CPF e código;
- criação de cadastro provisório quando não houver correspondência segura;
- detecção de conflitos de horário;
- criação dos agendamentos selecionados;
- trilha de auditoria da importação.
