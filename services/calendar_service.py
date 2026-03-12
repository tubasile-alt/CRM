import os
import datetime
from services.google_calendar import _get_calendar_service

TRANSPLANT_CALENDAR_ID = os.getenv('TRANSPLANT_CALENDAR_ID', 'primary')


def _find_calendar_by_email(service, email):
    """
    Procura um calendário pelo email da conta.
    Retorna o ID do calendário ou None.
    """
    try:
        calendars = service.calendarList().list().execute()
        for cal in calendars.get('items', []):
            if cal.get('id') == email or cal.get('summary') == email:
                return cal.get('id')
        return None
    except Exception:
        return None


def create_transplant_surgery_event(patient_name, surgery_date, planning_snapshot, phone=None, cpf=None, right_card_snapshot=None):
    """
    Cria um evento no Google Calendar via Replit Connector.
    """
    try:
        service = _get_calendar_service()
        
        # Tenta encontrar o calendário específico, senão usa 'primary'
        calendar_id = TRANSPLANT_CALENDAR_ID
        if calendar_id != 'primary':
            found_id = _find_calendar_by_email(service, calendar_id)
            if found_id:
                calendar_id = found_id
        
        # Título do evento
        summary = f"Transplante Capilar — {patient_name}"
        
        # Descrição detalhada
        description = f"Paciente: {patient_name}\n"
        if phone: description += f"Telefone: {phone}\n"
        if cpf: description += f"CPF: {cpf}\n"
        description += f"\n--------------------------------------------------\n"
        description += f"PLANEJAMENTO CIRÚRGICO (snapshot):\n{planning_snapshot}"
        
        if right_card_snapshot:
            description += "\n\n--------------------------------------------------\n"
            description += f"INFORMAÇÕES DO CARD FIXO (lado direito):\n{right_card_snapshot}"
        
        # Horário: 08:00 às 13:00 (5h de duração padrão para transplante)
        start_time = datetime.datetime.combine(surgery_date, datetime.time(8, 0))
        end_time = datetime.datetime.combine(surgery_date, datetime.time(13, 0))
        
        # Criar evento
        event = {
            'summary': summary,
            'description': description,
            'start': {
                'dateTime': start_time.isoformat(),
                'timeZone': 'America/Sao_Paulo'
            },
            'end': {
                'dateTime': end_time.isoformat(),
                'timeZone': 'America/Sao_Paulo'
            }
        }

        created = service.events().insert(calendarId=calendar_id, body=event).execute()
        
        return True, created.get('id')
    except Exception as e:
        print(f"Erro ao criar evento no Google Calendar: {e}")
        return False, str(e)
