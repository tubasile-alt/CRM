# Sistema Médico Web - Clínica Basile CRM Médico

## Visão Geral

Sistema médico completo desenvolvido em Flask (Python) para gestão de consultas, prontuário eletrônico e CRM médico. Totalmente em português e otimizado para uso em navegadores (desktop e tablets).

## Estrutura do Projeto

```
/
├── app.py                 # Núcleo Flask com rotas e APIs
├── config.py              # Configurações (banco, timezone, secret key)
├── models.py              # Modelos de dados (SQLAlchemy ORM)
├── requirements.txt       # Dependências Python
├── templates/             # Interface HTML (Bootstrap 5)
│   ├── base.html
│   ├── login.html
│   ├── dashboard.html
│   ├── agenda.html
│   ├── prontuario.html
│   └── chat.html
├── static/
│   ├── css/
│   │   └── style.css      # Estilos customizados
│   └── js/
│       ├── main.js        # Funções utilitárias
│       ├── agenda.js      # FullCalendar e gestão de agenda
│       ├── prontuario.js  # Ditado por voz e cronômetro
│       └── chat.js        # Chat em tempo real
└── medcrm.db              # Banco de dados SQLite
```

## Funcionalidades Implementadas

### Autenticação
- Sistema de login com Flask-Login
- Dois perfis: Médico e Secretária
- Médico: acesso total (dashboard, agenda, prontuário, chat)
- Secretária: acesso à agenda e chat

### Dashboard Médico
- Estatísticas do dia em tempo real
- Contadores: agendados, confirmados, atendidos, faltaram
- Chat rápido integrado
- Espaço reservado para gráficos de CRM

### Agenda Médica
- FullCalendar com visualizações: mensal, semanal, diária e lista
- Status com cores distintas:
  - Cinza: agendado
  - Azul: confirmado
  - Verde: atendido
  - Vermelho: faltou
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

### Chat Interno
- Comunicação entre médico e secretária
- Atualização automática a cada 5 segundos
- Mensagens persistidas no banco de dados

## Tecnologias Utilizadas

### Backend
- Flask 3.0.0
- Flask-Login 0.6.3
- Flask-SQLAlchemy 3.1.1
- Flask-WTF 1.2.1
- SQLite (SQLAlchemy ORM)
- Pytz (timezone America/Sao_Paulo)

### Frontend
- Bootstrap 5.3.0
- Bootstrap Icons 1.10.0
- FullCalendar 6.1.9
- Web Speech API (nativa do navegador)
- JavaScript ES6+

## Banco de Dados

### Tabelas
- **User**: médicos e secretárias
- **Patient**: pacientes
- **Appointment**: agendamentos
- **Note**: anotações do prontuário
- **Procedure**: lista de procedimentos
- **Indication**: procedimentos indicados/realizados
- **Tag**: tags disponíveis
- **PatientTag**: tags associadas aos pacientes
- **ChatMessage**: mensagens do chat

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

A aplicação estará disponível em: http://0.0.0.0:5000

## Configuração

O sistema utiliza o timezone `America/Sao_Paulo` e todas as datas são formatadas no padrão brasileiro.

A secret key é obtida da variável de ambiente `SESSION_SECRET` ou usa uma chave de desenvolvimento.

## Próximas Funcionalidades (Roadmap)

1. Gráficos de CRM com taxa de conversão de procedimentos
2. Relatórios de produtividade
3. Integração com feriados nacionais brasileiros
4. Notificações automáticas para pacientes
5. Migração para PostgreSQL (produção)
6. Sistema de backup automático
7. Exportação de relatórios em PDF

## Data de Criação

10 de novembro de 2025

## Segurança Implementada

- **Proteção CSRF**: Implementada via Flask-WTF em todas as rotas de modificação de dados
- **Autenticação robusta**: Flask-Login com hash seguro de senhas (Werkzeug)
- **Controle de acesso**: Rotas protegidas com @login_required
- **Separação de perfis**: Médico tem acesso total, secretária gerencia apenas agenda e chat

## Gestão de Agenda Multi-Usuário

A secretária pode visualizar e gerenciar a agenda do médico. O sistema automaticamente:
- Identifica se o usuário é médico ou secretária
- Permite que a secretária crie/edite agendamentos para o médico
- Mantém os agendamentos associados ao médico correto

## Notas Importantes

- O ditado por voz funciona apenas em HTTPS (como Replit)
- O sistema está configurado para rodar na porta 5000
- Cache desabilitado para desenvolvimento ágil
- Responsivo para notebooks e tablets
- Token CSRF incluído automaticamente em todas requisições AJAX
