# Sistema Médico Web - Clínica Basile CRM Médico

## Visão Geral

Sistema médico completo desenvolvido em Flask (Python) para gestão de consultas, prontuário eletrônico e CRM médico. Totalmente em português e otimizado para uso em navegadores (desktop e tablets).

**Nova Arquitetura Modular:** Refatorado com blueprints e serviços separados para melhor manutenibilidade e escalabilidade.

## Estrutura do Projeto

```
/
├── app.py                      # Núcleo Flask com rotas principais e APIs
├── config.py                   # Configurações (banco, timezone, secret key, email)
├── models.py                   # Modelos de dados (SQLAlchemy ORM)
├── requirements.txt            # Dependências Python
├── instance/
│   └── medcrm.db              # Banco de dados SQLite (pasta criada automaticamente)
├── routes/                     # Blueprints modulares (NEW)
│   ├── surgical_map.py        # Rotas do mapa cirúrgico
│   ├── waiting_room.py        # Rotas de check-in/checkout
│   └── settings.py            # Rotas de configurações
├── services/                   # Serviços de negócio (NEW)
│   ├── email_service.py       # Serviço de envio de emails
│   ├── waiting_service.py     # Lógica de tempo de espera
│   └── surgery_service.py     # Validação de conflitos cirúrgicos
├── utils/                      # Utilitários (NEW)
│   ├── backup.py              # Script de backup automático do banco
│   └── exports/
│       ├── pdf_export.py      # Exportação de relatórios em PDF
│       └── excel_export.py    # Exportação de relatórios em Excel
├── templates/                  # Interface HTML (Bootstrap 5)
│   ├── base.html              # Template base com navegação
│   ├── login.html             # Página de login
│   ├── dashboard.html         # Dashboard do médico
│   ├── agenda.html            # Agenda médica com multi-doctor support
│   ├── prontuario.html        # Prontuário eletrônico
│   ├── chat.html              # Chat interno
│   ├── surgical_map.html      # Mapa cirúrgico (NEW)
│   ├── waiting_room.html      # Sala de espera (NEW)
│   └── settings.html          # Página de configurações (NEW)
└── static/
    ├── css/
    │   └── style.css          # Estilos customizados
    └── js/
        ├── main.js            # Funções utilitárias
        ├── agenda.js          # FullCalendar e gestão de agenda
        ├── prontuario.js      # Ditado por voz e cronômetro
        └── chat.js            # Chat em tempo real
```

## Funcionalidades Implementadas

### Autenticação
- Sistema de login com Flask-Login
- Dois perfis: Médico e Secretária
- Médico: acesso total (dashboard, agenda, prontuário, chat, mapa cirúrgico, configurações)
- Secretária: acesso à agenda, chat e sala de espera

### Dashboard Médico
- Estatísticas do dia em tempo real
- Contadores: agendados, confirmados, atendidos, faltaram
- Chat rápido integrado
- Espaço reservado para gráficos de CRM

### Agenda Médica (Multi-Doctor Support) ⭐ NEW
- **Suporte a múltiplos médicos:**
  - Secretárias podem selecionar qual médico ao criar agendamentos
  - Filtros por médico (botões "Todos" / "Dr. Nome")
  - Cores personalizadas por médico (layers coloridos)
- **FullCalendar** com visualizações: mensal, semanal, diária e lista
- **Sistema de cores duplo:**
  - Background: cor do médico (azul, verde, roxo, etc.)
  - Borda: cor do status (cinza=agendado, azul=confirmado, verde=atendido, vermelho=faltou)
- **Check-in/Checkout workflow:** ⭐ NEW
  - Botões de check-in e check-out nos detalhes do agendamento
  - Contador de espera em tempo real (atualiza a cada 30 segundos)
  - Cálculo automático de tempo de espera
- **Exportação e compartilhamento:** ⭐ NEW
  - Exportar PDF com lista de agendamentos
  - Exportar Excel (XLSX) com dados detalhados
  - Enviar relatórios por email (PDF e/ou Excel anexados)
- Criação, edição e exclusão de agendamentos
- Arrastar e soltar para reagendar
- Impressão de agenda
- Integração com feriados nacionais (preparado)

### Prontuário Eletrônico
- Quatro abas: Queixa Principal, Anamnese, Consulta, Conduta
- Ditado por voz em português brasileiro (Web Speech API)
- Cronômetro de atendimento
- Gestão de procedimentos:
  - Ulthera
  - Morpheus8
  - Sculptra
  - Exilis
  - Neo
  - Entone
- Indicação e realização de procedimentos (CRM)
- Sistema de tags para pacientes:
  - Pré-operatório
  - VIP
  - Potencial Sculptra
  - Retorno
  - Primeira Consulta
- Histórico completo de anotações

### Mapa Cirúrgico Semanal ⭐ NEW
- Visualização de cirurgias agendadas por semana
- Gestão de salas cirúrgicas (Centro Cirúrgico 1, 2, 3)
- **Validação de conflitos:**
  - Detecta conflitos de sala (mesma sala, mesmo horário)
  - Detecta conflitos de médico (médico em duas cirurgias simultaneamente)
  - Alerta automático ao tentar criar cirurgia conflitante
- Informações completas: paciente, procedimento, médico, sala, horário
- Interface intuitiva para agendar e gerenciar cirurgias

### Sala de Espera Digital ⭐ NEW
- **Dashboard de espera** com estatísticas em tempo real:
  - Total aguardando
  - Tempo médio de espera
  - Próximo paciente
- **Lista de pacientes:**
  - Nome, horário agendado, tempo esperando
  - Status (aguardando / em atendimento)
  - Ações rápidas (atender, cancelar)
- **Workflow completo:**
  - Check-in: marca chegada do paciente
  - Check-out: marca atendimento concluído e calcula tempo de espera
- Integração total com agenda médica

### Chat Interno
- Comunicação entre médico e secretária
- Atualização automática a cada 5 segundos
- Mensagens persistidas no banco de dados

### Configurações e Backup ⭐ NEW
- **Página de configurações:**
  - Backup manual do banco de dados
  - Configurações de email (servidor SMTP)
  - Preferências por médico (cores, visibilidade de layers)
- **Sistema de backup:**
  - Script automático (`utils/backup.py`)
  - Backup compactado (.gz) com timestamp
  - Preservação dos últimos 30 backups
  - Comando: `python utils/backup.py`

### Exportação e Compartilhamento ⭐ NEW
- **PDF (reportlab):**
  - Relatórios profissionais em PDF
  - Cabeçalho com logo da clínica
  - Lista formatada de agendamentos
- **Excel (openpyxl):**
  - Planilhas com dados detalhados
  - Formatação automática (cabeçalhos, bordas, cores)
  - Pronto para análise em Excel/Google Sheets
- **Email (Flask-Mail):**
  - Envio automático de relatórios
  - Suporte a múltiplos anexos (PDF + Excel)
  - Corpo de email formatado em HTML
  - Configuração via variáveis de ambiente

## Tecnologias Utilizadas

### Backend
- Flask 3.0.0
- Flask-Login 0.6.3
- Flask-SQLAlchemy 3.1.1
- Flask-WTF 1.2.1
- Flask-Mail 0.10.0 ⭐ NEW
- SQLite (SQLAlchemy ORM)
- Pytz (timezone America/Sao_Paulo)
- ReportLab 4.0.7 (geração de PDF) ⭐ NEW
- Pillow 10.1.0 (processamento de imagens) ⭐ NEW
- OpenPyXL 3.1.2 (geração de Excel) ⭐ NEW

### Frontend
- Bootstrap 5.3.0
- Bootstrap Icons 1.10.0
- FullCalendar 6.1.9
- Web Speech API (nativa do navegador)
- JavaScript ES6+

## Banco de Dados

### Localização
O banco de dados fica em `./instance/medcrm.db` (SQLAlchemy cria a pasta `instance/` automaticamente).

### Tabelas
- **User**: médicos e secretárias
- **Patient**: pacientes
- **Appointment**: agendamentos (com campos: `waiting`, `checked_in_time`, `room`) ⭐ NEW
- **Note**: anotações do prontuário
- **Procedure**: lista de procedimentos
- **Indication**: procedimentos indicados/realizados
- **Tag**: tags disponíveis
- **PatientTag**: tags associadas aos pacientes
- **ChatMessage**: mensagens do chat
- **Surgery**: cirurgias agendadas ⭐ NEW
- **OperatingRoom**: salas cirúrgicas ⭐ NEW
- **DoctorPreference**: preferências e cores por médico ⭐ NEW

## Credenciais de Demonstração

- **Médico**: arthur@clinicabasiledemo.com / 123456
- **Secretária**: secretaria@clinicabasiledemo.com / 123456

## Comandos Úteis

### Inicializar banco de dados
```bash
flask init-db
```

### Executar aplicação
```bash
python app.py
```

### Backup manual
```bash
python utils/backup.py
```

A aplicação estará disponível em: http://0.0.0.0:5000

## Configuração

### Timezone
O sistema utiliza o timezone `America/Sao_Paulo` e todas as datas são formatadas no padrão brasileiro.

### Variáveis de Ambiente
- `SESSION_SECRET`: Secret key para sessões (obrigatória em produção)
- `MAIL_SERVER`: Servidor SMTP para envio de emails
- `MAIL_PORT`: Porta do servidor SMTP
- `MAIL_USERNAME`: Usuário do email
- `MAIL_PASSWORD`: Senha do email
- `MAIL_USE_TLS`: Usar TLS (True/False)

## Próximas Funcionalidades (Roadmap)

1. ~~Sistema de backup automático~~ ✅ IMPLEMENTADO
2. ~~Exportação de relatórios em PDF/Excel~~ ✅ IMPLEMENTADO
3. ~~Mapa cirúrgico com validação de conflitos~~ ✅ IMPLEMENTADO
4. ~~Check-in/checkout de pacientes~~ ✅ IMPLEMENTADO
5. ~~Suporte a múltiplos médicos~~ ✅ IMPLEMENTADO
6. Gráficos de CRM com taxa de conversão de procedimentos
7. Relatórios de produtividade
8. Integração com feriados nacionais brasileiros
9. Notificações automáticas para pacientes (SMS/Email)
10. Migração para PostgreSQL (produção)

## Data de Atualização

**Criado:** 10 de novembro de 2025  
**Última Atualização:** 10 de novembro de 2025 (Implementação de funcionalidades avançadas)

## Segurança Implementada

- **Proteção CSRF**: Implementada via Flask-WTF em todas as rotas de modificação de dados
- **Autenticação robusta**: Flask-Login com hash seguro de senhas (Werkzeug)
- **Controle de acesso**: Rotas protegidas com @login_required
- **Separação de perfis**: Médico tem acesso total, secretária gerencia apenas agenda, chat e sala de espera
- **Backup regular**: Sistema de backup com preservação de histórico
- **Validação de dados**: Todos os formulários com validação client-side e server-side

## Gestão de Agenda Multi-Médico ⭐ NEW

O sistema agora suporta múltiplos médicos simultaneamente:

### Para Secretárias:
- Ao criar agendamento, seleciona qual médico via dropdown
- Pode filtrar agenda por médico específico ou ver todos
- Pode exportar/enviar emails filtrando por médico
- Cores diferentes para cada médico facilitam identificação visual

### Para Médicos:
- Veem automaticamente apenas suas próprias consultas
- Podem configurar cor personalizada para seus agendamentos
- Exportações/emails incluem apenas seus agendamentos

### Sistema de Cores:
- Cada médico tem uma cor única configurável
- Background do evento = cor do médico
- Borda do evento = cor do status
- Exemplo: "Dr. Arthur (azul) com paciente confirmado (borda azul escuro)"

## Arquitetura Modular ⭐ NEW

### Blueprints
O sistema usa Flask Blueprints para modularização:
- `routes/surgical_map.py`: Rotas do mapa cirúrgico
- `routes/waiting_room.py`: Rotas de check-in/checkout
- `routes/settings.py`: Rotas de configurações

### Services
Lógica de negócio separada em serviços:
- `services/email_service.py`: Envio de emails
- `services/waiting_service.py`: Cálculos de tempo de espera
- `services/surgery_service.py`: Validação de conflitos

### Utils
Utilitários e exportadores:
- `utils/backup.py`: Backup automático
- `utils/exports/pdf_export.py`: Geração de PDFs
- `utils/exports/excel_export.py`: Geração de planilhas Excel

## Notas Importantes

- O ditado por voz funciona apenas em HTTPS (como Replit)
- O sistema está configurado para rodar na porta 5000
- Cache desabilitado para desenvolvimento ágil
- Responsivo para notebooks e tablets
- Token CSRF incluído automaticamente em todas requisições AJAX
- **Banco de dados está em ./instance/medcrm.db** (não em ./medcrm.db)
- Backups são salvos em ./backups/ com timestamp
- PDFs gerados usam reportlab (WeasyPrint não funciona devido a dependências do sistema)
- O contador de espera atualiza automaticamente a cada 30 segundos

## Crítico: Segurança de Dados

⚠️ **AVISO IMPORTANTE:** O banco de dados contém informações médicas sensíveis.

- Sempre faça backup antes de alterações importantes
- Use o script `utils/backup.py` regularmente
- Backups são mantidos automaticamente (últimos 30)
- Em produção, migre para PostgreSQL com backup automático
- NUNCA exponha o arquivo do banco de dados publicamente
