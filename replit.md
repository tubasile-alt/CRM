# CRM Médico - Clínica Basile

## 📋 Visão Geral
Sistema completo de gestão de clínica dermatológica e cirurgia plástica com agendamento, prontuários, checkout de pagamentos e controle de acesso por papéis.

## 🏗️ Arquitetura
- **Backend:** Flask + SQLAlchemy
- **Banco de Dados:** PostgreSQL (produção) + SQLite (local)
- **Frontend:** Jinja2 + HTML/CSS/JavaScript
- **Autenticação:** Flask-Login com roles (médico, secretária)

## 📊 Status Atual (02/12/2025)
- ✅ Migração de dados do SQLite para PostgreSQL completa
- ✅ Interface de agenda diária com mini-calendário 3D
- ✅ Layout flexbox (sem overlapping)
- ✅ Blocos de agendamento com 3 colunas: Nome | Tipo Paciente | Tipo Consulta
- ✅ Sistema de backup automático implementado
- ✅ **✅ COMPLETO**: Aba Cirurgias implementada e funcional para Transplante Capilar
  - Modelo: `TransplantSurgeryRecord` em models.py
  - Blueprint: `patient_bp` em routes/patient.py com 3 endpoints
  - Endpoints: GET, POST, DELETE para cirurgias
  - Interface: Aba independente com formulário e histórico
  - Funcionalidades: Registrar cirurgias ✅, calcular tempo desde cirurgia ✅, criar evolução vinculada ✅

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
1. **Agenda Diária** - Visualização por horários
2. **Prontuário** - Histórico completo do paciente com evoluções
3. **Agendamento** - Criação e edição de consultas
4. **Checkout** - Sistema de pagamento por procedimento
5. **Chat** - Comunicação interna entre usuários
6. **Controle de Acesso** - Médicos veem seus pacientes, secretárias veem todos
7. **Registro de Cirurgias** - Para pacientes de Transplante Capilar ✅

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

## 🔒 Segurança
- Senhas com hash seguro
- CSRF protection ativada
- Session cookies com HTTPOnly
- Acesso controlado por papéis
- Acesso a cirurgias verificado por doctor_id
- Backups comprimidos e versionados
