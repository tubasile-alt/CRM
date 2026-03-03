import os
import datetime
from replit.integrations.google_calendar import GoogleCalendar

def create_transplant_surgery_event(patient_name, surgery_date, planning_snapshot, phone=None, cpf=None):
    """
    Cria um evento no Google Calendar via Replit Connector.
    """
    try:
        calendar = GoogleCalendar()
        
        # Título do evento
        summary = f"Transplante Capilar — {patient_name}"
        
        # Descrição detalhada
        description = f"Paciente: {patient_name}\n"
        if phone: description += f"Telefone: {phone}\n"
        if cpf: description += f"CPF: {cpf}\n"
        description += f"\n--------------------------------------------------\n"
        description += f"PLANEJAMENTO CIRÚRGICO (snapshot):\n{planning_snapshot}"
        
        # Horário: 08:00 às 13:00 (5h de duração padrão para transplante)
        start_time = datetime.datetime.combine(surgery_date, datetime.time(8, 0))
        end_time = datetime.datetime.combine(surgery_date, datetime.time(13, 0))
        
        # Criar evento
        event = calendar.create_event(
            summary=summary,
            description=description,
            start=start_time.isoformat(),
            end=end_time.isoformat(),
            timezone="America/Sao_Paulo"
        )
        
        return True, event.get('id')
    except Exception as e:
        print(f"Erro ao criar evento no Google Calendar: {e}")
        return False, str(e)
