# CRM Médico - Clínica Basile

## 📋 Visão Geral
Sistema completo de gestão de clínica dermatológica e cirurgia plástica com agendamento, prontuários, checkout de pagamentos e controle de acesso por papéis.

## 🏗️ Arquitetura
- **Backend:** Flask + SQLAlchemy
- **Banco de Dados:** PostgreSQL (produção) + SQLite (local)
- **Frontend:** Jinja2 + HTML/CSS/JavaScript
- **Autenticação:** Flask-Login com roles (médico, secretária)

## 📊 Status Atual (09/02/2026)
- ✅ Migração de dados do SQLite para PostgreSQL completa
- ✅ Interface de agenda diária com mini-calendário
- ✅ Layout flexbox (sem overlapping)
- ✅ Blocos de agendamento com 3 colunas: Nome | Tipo Paciente | Tipo Consulta
- ✅ Sistema de backup automático implementado
- ✅ **Aba Cirurgias** implementada e funcional para Transplante Capilar
- ✅ **Idade do paciente** exibida ao lado do nome no prontuário
- ✅ **Botão Editar Cadastro** - Permite edição de dados do paciente (médicos e secretárias)
- ✅ **Checkout corrigido** - Modal de pagamento funcionando na aba Checkout
- ✅ **Indicação de Transplante** - Campo "Sim/Não" como primeiro item na aba Transplante Capilar
- ✅ **Checkout melhorado** - Valores discriminados (consulta + procedimentos separados)
- ✅ **Toggle de cobrança** - Checkbox para cobrar ou não cobrar consulta no checkout
- ✅ **Badge de pendências** - Número de checkouts pendentes visível na aba Agenda
- ✅ **Slots de 15 minutos** - Agenda mostra intervalos de 15 em 15 minutos
- ✅ **Sala de Espera** - Lista de pacientes aguardando com cronômetro em tempo real
- ✅ **Botão Check In** - Botão verde para fazer check-in do paciente na agenda
- ✅ **Aba CRM** - Gestão de procedimentos com follow-up automático
- ✅ **Checkbox "Transplante Capilar Feminino"** - Opção adicionada à seção de planejamento cirúrgico
- ✅ **Checkbox "Dense Packing"** - Opção adicionada à seção de indicações cirúrgicas
- ✅ **Performance otimizada** - Batch updates e índices de banco de dados implementados
- ✅ **Cronômetro de Espera** - Timer em tempo real para sala de espera (atualiza a cada segundo)
- ✅ **Agendamento de Cirurgias** - Opção "Cirurgia" no dropdown de tipo de paciente, cria automaticamente no Mapa Cirúrgico
- ✅ **Integração DermaScribe** - Botão "Prescrever" na aba Conduta abre DermaScribe com nome do paciente
- ✅ **Modelo Prescription** - Tabela para salvar receitas emitidas vinculadas ao paciente
- ✅ **APIs de Receitas** - POST/GET para salvar e listar receitas do paciente
- ✅ **DermaScribe INTERNO** - Sistema de receituário integrado ao CRM (não mais externo)
- ✅ **Modelos Medication/MedicationUsage** - Tabelas para banco de medicamentos e rastreamento de prescrições
- ✅ **Link DermaScribe no menu** - Acesso direto ao receituário pelo menu principal (apenas médicos)
- ✅ **Persistência de Prescrições** - Receitas salvas diretamente no prontuário do paciente
- ✅ **Analytics de Medicamentos** - Rastreamento de uso para estatísticas de prescrição
- ✅ **Webcam Foto Paciente** - Captura de foto via webcam no agendamento (novo e edição)
- ✅ **Evoluções Pós-Cirúrgicas** - Formulários automáticos de 7 dias (complicações) e 1 ano (resultado)
- ✅ **Dashboard Cirurgias** - Estatísticas de necrose, infecções, resultados no dashboard
- ✅ **CRM Follow-up Cirúrgico** - Lembrete automático para pacientes que precisam de nova cirurgia
- ✅ **Separação Check-out/Remover Espera** - `undo_check_in()` não muda status, `check_out()` marca como atendido
- ✅ **window.appointmentId** - Variável global para compartilhamento entre template e JS externo
- ✅ **WeasyPrint PDF** - Rota /pdf para geração de PDF real de receitas (sem depender do browser)
- ✅ **Google Sheets Integration** - Procedimentos realizados são enviados automaticamente para planilha Google (webhook n8n)
- ✅ **Google Calendar Integration** - Cirurgias agendadas criam evento automático no Google Calendar com nome do paciente e descrição
- ✅ **Módulo CP (Cirurgia Plástica)** - Prontuário dedicado com tabs Queixa/Planejamento/Orçamento/Retorno/Histórico, timer, chips de procedimento/técnica, áreas de lipo, módulo de implante e cálculo de orçamento
- ✅ **Controle de Acesso DP** - Modelo PatientDoctor para vínculo médico-paciente; `role_clinico` (CP/DERM/SECRETARY/ADMIN) no User; service `authz.py` com `can_view_dp`/`can_edit_dp`
- ✅ **APIs CP** - Blueprint `cp.py`: start/save/get/finalize encounter, histórico por dp_id; autosave a cada 30s
- ✅ **Rotas DP** - `/prontuario/dp/<dp_id>` renderiza `prontuario_cp.html` (CP) ou `prontuario.html` (DERM read-only); secretárias veem `select_dp.html`; médicos CP são redirecionados automaticamente da rota padrão
- ✅ **CRM integrado com dp_id** - Painel de agendados/planejados/realizados usa dp_id para abrir o prontuário CP correto

## 🛡️ SISTEMA DE BACKUP (CRÍTICO)

### Proteção de Dados
Para garantir que os dados NUNCA sejam perdidos, foi implementado um sistema robusto de backup:

#### 1. **Backup Automático**
- Executado a cada 30 minutos durante uso da aplicação
- Ocorre automaticamente na inicialização (`init_backup.py`)
- Não interrompe o funcionamento da aplicação

#### 2. **Comandos de Backup**

```bash
# Fazer backup manual
python commands/backup_cli.py backup

# Listar todos os backups
python commands/backup_cli.py list

# Ver estatísticas
python commands/backup_cli.py stats

# Restaurar um backup
python commands/backup_cli.py restore --file sqlite_dump_20251125_161533.sql.gz
```

#### 3. **Inicialização com Backup**
Antes de iniciar a aplicação em produção:
```bash
python init_backup.py && python app.py
```

#### 4. **Localização de Backups**
- Todos os backups em: `./backups/`
- Log de backups: `./backups/backup_log.json`
- Máximo 50 backups mantidos automaticamente (mais antigos são removidos)

#### 5. **Tipos de Backup**
- **SQLite:** Dump SQL completo (comprimido com gzip)
- **PostgreSQL:** Dump completo via pg_dump

## 👥 Usuários Padrão
- **Dr. Arthur Basile** (Médico)
  - Email: `arthur@clinicabasiledemo.com`
  - Senha: [sua senha]

- **Secretária**
  - Email: `secretaria@clinicabasiledemo.com`
  - Senha: [sua senha]

## 🎨 Design da Agenda
- **Layout:** Flexbox com mini-calendário (280px) + agenda diária (flex: 1)
- **Mini-calendário:** Efeito 3D com perspectiva(1000px) e rotateY(-5deg)
- **Blocos:** Mostram Nome / Tipo Paciente / Tipo Consulta
- **Cores por tipo:** 
  - Amarelo: Particular
  - Azul: Retorno
  - Verde: UNIMED
  - Cinza: Cortesia
  - Vermelho: Transplante Capilar

## 🔧 Funcionalidades Principais
1. **Agenda Diária** - Visualização por horários (slots de 30 minutos)
2. **Prontuário** - Histórico completo do paciente com evoluções
3. **Agendamento** - Criação e edição de consultas
4. **Checkout** - Sistema de pagamento por procedimento
5. **Chat** - Comunicação interna entre usuários
6. **Controle de Acesso** - Médicos veem seus pacientes, secretárias veem todos
7. **Registro de Cirurgias** - Para pacientes de Transplante Capilar ✅
8. **Sala de Espera / Check-In** - Cronômetro de espera para pacientes ✅

## 🕐 Sistema de Sala de Espera (04/12/2025)

### Funcionalidades
- **Botão Check In** (verde) ao lado do tipo de consulta nos blocos de agendamento
- **Cronômetro automático** que conta o tempo de espera do paciente
- **Lista de espera** visível abaixo do mini calendário
- **Visível para médicos e secretárias**
- **Auto-remoção** quando o atendimento é finalizado

### API Endpoints
- `POST /api/checkin/<appointment_id>` - Fazer check-in do paciente
- `GET /api/waiting-room` - Listar pacientes aguardando
- `POST /api/checkout-waiting/<appointment_id>` - Remover da sala de espera

### Comportamento
1. Secretária clica em "Check In" no bloco de agendamento
2. Paciente aparece na lista de espera com cronômetro
3. Cronômetro atualiza automaticamente (mostra minutos de espera)
4. Clicar no paciente na lista abre o prontuário
5. Ao finalizar atendimento, paciente sai automaticamente da lista

## 📁 Estrutura de Pastas
```
/
├── app.py                  # Aplicação principal
├── config.py              # Configurações
├── models.py              # Modelos do banco
├── requirements.txt       # Dependências
├── init_backup.py         # Script de inicialização com backup
├── commands/
│   └── backup_cli.py      # CLI de backup/restauração
├── utils/
│   └── database_backup.py # Sistema de backup
├── routes/                # Blueprints de rotas
│   ├── __init__.py
│   ├── patient.py         # Rotas de paciente (cirurgias)
│   ├── surgical_map.py
│   ├── settings.py
│   └── waiting_room.py
├── templates/             # Templates HTML
├── static/               # CSS, JS, imagens
│   └── js/
│       └── surgeries.js   # JavaScript para cirurgias
├── backups/              # Diretório de backups
└── instance/
    └── medcrm.db         # Banco SQLite local
```

## 🚀 Como Iniciar
```bash
# Instalar dependências
pip install -r requirements.txt

# Fazer backup e iniciar
python init_backup.py && python app.py
```

## ⚠️ IMPORTANTE: Proteção de Dados
**NUNCA** faça upgrade ou mudanças estruturais sem:
1. Executar `python init_backup.py` primeiro
2. Verificar que o backup foi criado com sucesso
3. Só então fazer as alterações

Todos os dados de pacientes são sensíveis e críticos para operação clínica.

## 📝 Notas de Desenvolvimento - Aba Cirurgias (02/12/2025)

### ✅ Implementação Completa
- ✅ Criado modelo `TransplantSurgeryRecord` em models.py
- ✅ Criado blueprint de paciente (`routes/patient.py`) com 3 rotas:
  - `GET /api/patient/<id>/surgeries` - Carrega histórico de cirurgias
  - `POST /api/patient/<id>/surgery` - Cria nova cirurgia
  - `DELETE /api/patient/<id>/surgery` - Remove cirurgia
- ✅ Implementado sistema JavaScript com:
  - Validação de formulário
  - Contador automático de tempo desde cirurgia
  - Carregamento e renderização de histórico
  - Botão para criar evolução vinculada
  - Exclusão de cirurgias

### 🔧 Correção Realizada
- **Problema:** Rotas definidas em app.py não estavam sendo registradas (retornando 404)
- **Solução:** Criado blueprint dedicado (`routes/patient.py`) e registrado no Flask
- **Resultado:** Todas as rotas agora funcionam (GET 200, POST 200, DELETE funcionando)

### ✅ Testes Realizados
- Salvamento de cirurgia: ✅ Funciona (POST status 200)
- Carregamento de histórico: ✅ Funciona (GET status 200)
- Contador automático: ✅ Calcula corretamente ("27/11/2025 - Cirurgia recente")
- Dados persistem no banco: ✅ Cirurgia salva com ID, data, dados e observações

## 🚀 Otimizações de Performance (11/12/2025)

### Banco de Dados
- ✅ Batch updates para procedimentos cosmético (N queries → 1 query)
- ✅ Índices criados em tabelas críticas:
  - `follow_up_reminder` (patient_id, procedure_name)
  - `follow_up_reminder` (status)
  - `cosmetic_procedure_plan` (note_id)
  - `indication` (note_id)
  - `note` (patient_id, category)
- ✅ `synchronize_session=False` para evitar queries adicionais

### Endpoint de Salvamento
- Otimizado endpoint `/api/prontuario/<patient_id>/finalizar`
- Batch processing de follow-up reminders
- Redução de queries de banco em ~70%

## 🔒 Segurança
- Senhas com hash seguro
- CSRF protection ativada
- Session cookies com HTTPOnly
- Acesso controlado por papéis
- Acesso a cirurgias verificado por doctor_id
- Backups comprimidos e versionados
