# Sistema Médico Web - Clínica Basile CRM Médico

## Overview

Sistema médico completo desenvolvido em Flask (Python) para gestão de consultas, prontuário eletrônico e CRM médico. O projeto foi refatorado com uma arquitetura modular para melhor manutenibilidade e escalabilidade. Ele oferece funcionalidades como agendamento multi-médico, prontuário eletrônico especializado (Dermatologia, Cosmiatria, Transplante Capilar), mapa cirúrgico com validação de conflitos, sala de espera digital, chat interno e ferramentas de exportação/backup. O sistema é otimizado para navegadores (desktop e tablets), totalmente em português, e foca na segurança dos dados médicos.

## User Preferences

- Eu prefiro que as explicações sejam detalhadas e que o agente me mantenha informado sobre as decisões importantes.
- Prefiro que o agente não faça alterações nos arquivos de configuração (`config.py`) ou nos modelos de dados (`models.py`) sem minha aprovação explícita.
- Peço que o agente priorize a segurança dos dados e a validação de entrada ao implementar novas funcionalidades.
- Não faça alterações na pasta `instance/` nem no arquivo `app.py` sem minha instrução.
- Prefiro que o agente adicione comentários claros e concisos ao código quando implementar novas funcionalidades ou modificar as existentes.

## System Architecture

### UI/UX Decisions
The front-end utilizes Bootstrap 5.3.0 for responsive design and Bootstrap Icons for iconography. FullCalendar 6.1.9 is integrated for the medical agenda, supporting multi-doctor views with customizable colors for doctors and appointment statuses. The design prioritizes a clear and intuitive interface for medical professionals and secretaries, including interactive elements like Norwood classification for hair transplants and dynamic planning tables for aesthetic procedures.

### Technical Implementations
- **Authentication**: Flask-Login handles user authentication with two profiles (Médico, Secretária), using secure password hashing and CSRF protection via Flask-WTF.
- **Multi-Doctor Agenda**: Implemented with FullCalendar, supporting multiple doctors, customizable colors per doctor, dual coloring (background for doctor, border for status), check-in/checkout workflow, real-time wait time calculation, and appointment type classification (Unimed, Particular, Cortesia).
- **Electronic Health Record (EHR)**:
    - **Patologia (Dermatology)**: Four specialized tabs (Queixa Principal, Anamnese/Exame Físico, Diagnóstico, Conduta) with voice dictation support. Traditional procedure indication system with "Procedimentos Indicados" section visible only in this category.
    - **Cosmiatria**: Pre-filled anamnesis, exclusive Clinical Planning tab (Planejamento) before Conduta tab. Features 14 cosmetic procedures (Botox, Preenchimento, MDCodes, Pearl Fracionado, Ulthera, Morpheus, Sculptra, Radiesse, Harmonica, Prophilo, Neoemsculpt, Exilis, Entone, Peeling) with multi-checkbox selection, budget tracking (planned value + final budget), and execution status ("Feito/Não Feito") for CRM control. Conduta tab shows only selected procedures with budget fields and execution toggle. PDF budget generation available. Automated CRM follow-up reminders created when procedures are not executed, with smart rollover (superseded/completed) on subsequent visits.
    - **Transplante Capilar**: Visual Norwood classification (6 interactive cards: 1-6), previous transplant tracking question (ICB or other service), multi-check surgical planning, secure image uploads (JPG/PNG/GIF, max 5MB, MIME type validation), and automated post-operative review reminders.
- **Surgical Map**: Weekly visualization of surgeries, management of 4 operating rooms (Sala 1-4), fixed morning time slots (7AM, 10AM) Monday-Friday, and conflict validation (room and doctor conflicts).
- **Digital Waiting Room**: Real-time dashboard with waiting statistics, patient list, and full check-in/checkout workflow.
- **Internal Chat**: 1-on-1 directed messaging system with contact selection, per-user read tracking via MessageRead table, unread message badges (global and per-contact), and real-time auto-refresh polling. Messages are private and directed to specific recipients, with a clean two-panel interface (contact list + conversation area).
- **Configuration & Backup**: Manual database backup, SMTP email settings, and per-doctor preferences. Automated backup script (`utils/backup.py`) preserving the last 30 backups.
- **Export & Sharing**: Professional PDF reports (ReportLab) and detailed Excel spreadsheets (OpenPyXL), with automated email sending (Flask-Mail) supporting multiple attachments.

### Feature Specifications
- **Condensed Consultation History** (November 2025): Completely redesigned history system with accordion UI showing consultations grouped by date. Implementation uses deterministic `appointment_id` foreign key in Note model for reliable grouping, with precise temporal fallback (2-second window) for legacy data to separate multiple same-day consultations. Full details expand on click including: all note sections (queixa, anamnese, diagnostico, conduta), cosmetic procedures with execution status and Brazilian currency formatting (R$ 1.500,00), hair transplant planning with Norwood classification, and indicated/performed procedures for both Patologia and Cosmiatria. Badge system differentiates finalized consultations from drafts. Zero data loss guarantee via dual-path grouping strategy. Template intelligently detects procedure types (cosmetic_plans, hair_transplants, indications) regardless of category field, and hides placeholder text "[Conduta registrada via procedimentos]" when displaying procedure-only consultations.
- **Unified Finalization Workflow**: All medical records now use a single "Finalizar Atendimento" button located in the Conduta tab (November 2025). Individual "Salvar" buttons removed from all tabs. Requirements: (1) consultation timer must be started before finalization; (2) all data (queixa, anamnese, diagnostico, conduta, plus category-specific data) is saved atomically in a single transaction via `/api/prontuario/<id>/finalizar`; (3) each consultation creates new records for historical tracking (CosmeticProcedurePlan, HairTransplant, Indication); (4) follow-up reminders are managed intelligently (superseded or completed based on execution status); (5) all notes link to appointment_id for deterministic consultation grouping.
- **Grouped Cosmetic Procedures by Consultation Date** (November 2025): Complete visual reorganization of cosmetic procedures in the Planning panel. Procedures are now displayed in separated sections by consultation date, with clear visual headers showing date and procedure count. New endpoint `/api/prontuario/<id>/cosmetic-plans-grouped` groups procedures by `appointment_id` or `note_id`, returning consultation metadata (date, doctor, appointment reference). Frontend renders procedures in distinct visual blocks with color-coded headers: green "Nova Consulta (não salvo)" section for unsaved procedures, and gray sections for historical consultations. Clicking on a consultation in the history sidebar automatically highlights and scrolls to the corresponding procedure group with a smooth animation. This prevents confusion between procedures from different visits and eliminates automatic duplication of previous procedures when starting new consultations. All historical procedures remain visible for reference while maintaining clear temporal separation.
- **Real-time Updates**: Dashboard statistics, waiting room, and chat update automatically.
- **Dashboard Statistics Logic**: "Agendados" counts sum of both "agendado" and "confirmado" statuses. "Confirmados", "Atendidos", and "Faltaram" remain exclusive to their respective statuses.
- **Appointment Type System**: Each appointment can be classified as Unimed, Particular, or Cortesia (defaults to Particular). Migration script available at `migrations/add_appointment_type.py`.
- **Data Validation**: Client-side and server-side validation for all forms.
- **Timezone Management**: Uses `America/Sao_Paulo` for all date/time operations.
- **Security**: CSRF protection, robust authentication, access control, regular backups, and strict image upload validation.

### System Design Choices
The system is built on a modular architecture using Flask Blueprints for feature separation (e.g., surgical map, waiting room, settings) and a services layer (`services/`) for encapsulating business logic (e.g., email, waiting time, surgery conflicts). Utility functions for backup and export are separated into `utils/`. The database is SQLite for development, with a recommendation for PostgreSQL in production.

## External Dependencies

### Backend
-   **Flask**: 3.0.0
-   **Flask-Login**: 0.6.3
-   **Flask-SQLAlchemy**: 3.1.1 (ORM for SQLite)
-   **Flask-WTF**: 1.2.1 (Form handling and CSRF protection)
-   **Flask-Mail**: 0.10.0 (Email sending)
-   **Pytz**: (Timezone handling)
-   **ReportLab**: 4.0.7 (PDF generation)
-   **Pillow**: 10.1.0 (Image processing)
-   **OpenPyXL**: 3.1.2 (Excel generation)

### Frontend
-   **Bootstrap**: 5.3.0
-   **Bootstrap Icons**: 1.10.0
-   **FullCalendar**: 6.1.9
-   **Web Speech API**: (Browser-native for voice dictation)
-   **JavaScript**: ES6+

### Databases
-   **SQLite**: Used as the primary database (`./instance/medcrm.db`).