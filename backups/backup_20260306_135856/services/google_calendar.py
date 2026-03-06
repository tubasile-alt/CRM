import os
import threading
import requests as http_requests
from datetime import datetime, date, time, timedelta
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build


def _get_access_token():
    hostname = os.environ.get('REPLIT_CONNECTORS_HOSTNAME')
    if not hostname:
        raise Exception('REPLIT_CONNECTORS_HOSTNAME não configurado')

    repl_identity = os.environ.get('REPL_IDENTITY')
    web_repl_renewal = os.environ.get('WEB_REPL_RENEWAL')

    if repl_identity:
        x_replit_token = f'repl {repl_identity}'
    elif web_repl_renewal:
        x_replit_token = f'depl {web_repl_renewal}'
    else:
        raise Exception('Token de autenticação Replit não encontrado')

    resp = http_requests.get(
        f'https://{hostname}/api/v2/connection?include_secrets=true&connector_names=google-calendar',
        headers={
            'Accept': 'application/json',
            'X_REPLIT_TOKEN': x_replit_token
        },
        timeout=10
    )

    if resp.status_code != 200:
        raise Exception(f'Erro ao obter conexão Google Calendar: HTTP {resp.status_code}')

    data = resp.json()
    connection = (data.get('items') or [None])[0]

    if not connection:
        raise Exception('Google Calendar não conectado')

    settings = connection.get('settings', {})
    access_token = (
        settings.get('access_token')
        or settings.get('oauth', {}).get('credentials', {}).get('access_token')
    )

    if not access_token:
        raise Exception('Access token do Google Calendar não encontrado')

    return access_token


def _get_calendar_service():
    token = _get_access_token()
    creds = Credentials(token=token)
    return build('calendar', 'v3', credentials=creds, cache_discovery=False)


def _do_create_event(patient_name, procedure_name, surgery_date, start_time, end_time, notes=''):
    try:
        service = _get_calendar_service()

        if isinstance(surgery_date, date) and not isinstance(surgery_date, datetime):
            start_dt = datetime.combine(surgery_date, start_time)
            end_dt = datetime.combine(surgery_date, end_time)
        else:
            start_dt = surgery_date
            end_dt = surgery_date + timedelta(hours=2)

        event = {
            'summary': f'Cirurgia - {patient_name}',
            'description': f'Procedimento: {procedure_name}\nPaciente: {patient_name}\n{notes}'.strip(),
            'start': {
                'dateTime': start_dt.strftime('%Y-%m-%dT%H:%M:%S'),
                'timeZone': 'America/Sao_Paulo',
            },
            'end': {
                'dateTime': end_dt.strftime('%Y-%m-%dT%H:%M:%S'),
                'timeZone': 'America/Sao_Paulo',
            },
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'popup', 'minutes': 1440},
                    {'method': 'popup', 'minutes': 60},
                ],
            },
        }

        created = service.events().insert(calendarId='primary', body=event).execute()
        print(f"✓ Google Calendar: Evento criado - {patient_name} ({created.get('id')})")
        return created.get('id')
    except Exception as e:
        print(f"✗ Erro Google Calendar: {e}")
        return None


def create_surgery_event(patient_name, procedure_name, surgery_date, start_time, end_time, notes=''):
    t = threading.Thread(
        target=_do_create_event,
        args=(patient_name, procedure_name, surgery_date, start_time, end_time, notes),
        daemon=True
    )
    t.start()
