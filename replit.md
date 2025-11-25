# CRM Médico - Clínica Basile

## 📋 Visão Geral
Sistema completo de gestão de clínica dermatológica e cirurgia plástica com agendamento, prontuários, checkout de pagamentos e controle de acesso por papéis.

## 🏗️ Arquitetura
- **Backend:** Flask + SQLAlchemy
- **Banco de Dados:** PostgreSQL (produção) + SQLite (local)
- **Frontend:** Jinja2 + HTML/CSS/JavaScript
- **Autenticação:** Flask-Login com roles (médico, secretária)

## 📊 Status Atual (25/11/2025)
- ✅ Migração de dados do SQLite para PostgreSQL completa
- ✅ Interface de agenda diária com mini-calendário 3D
- ✅ Layout flexbox (sem overlapping)
- ✅ Blocos de agendamento com 3 colunas: Nome | Tipo Paciente | Tipo Consulta
- ✅ Sistema de backup automático implementado

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
2. **Prontuário** - Histórico completo do paciente
3. **Agendamento** - Criação e edição de consultas
4. **Checkout** - Sistema de pagamento por procedimento
5. **Chat** - Comunicação interna entre usuários
6. **Controle de Acesso** - Médicos veem sua agenda, secretárias veem todas

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
├── templates/             # Templates HTML
├── static/               # CSS, JS, imagens
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

## 📝 Notas de Desenvolvimento
- Dados migrados com sucesso do SQLite original para PostgreSQL
- 5 pacientes e agendamentos recuperados
- Sistema de backup protege contra qualquer perda de dados
- Mini-calendário com efeitos 3D melhora UX

## 🔒 Segurança
- Senhas com hash seguro
- CSRF protection ativada
- Session cookies com HTTPOnly
- Acesso controlado por papéis
- Backups comprimidos e versionados
