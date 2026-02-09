import os
import threading
import requests as http_requests
from datetime import datetime, timezone
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SPREADSHEET_TITLE = "CRM Clínica Basile - Procedimentos"
SHEET_HEADERS = [
    "Data", "Horário", "Paciente", "Procedimento", "Valor (R$)", "Tipo Consulta", "Status", "Médico"
]


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
        f'https://{hostname}/api/v2/connection?include_secrets=true&connector_names=google-sheet',
        headers={
            'Accept': 'application/json',
            'X_REPLIT_TOKEN': x_replit_token
        },
        timeout=10
    )

    if resp.status_code != 200:
        raise Exception(f'Erro ao obter conexão Google Sheets: HTTP {resp.status_code}')

    data = resp.json()
    connection = (data.get('items') or [None])[0]

    if not connection:
        raise Exception('Google Sheets não conectado')

    settings = connection.get('settings', {})
    access_token = (
        settings.get('access_token')
        or settings.get('oauth', {}).get('credentials', {}).get('access_token')
    )

    if not access_token:
        raise Exception('Access token do Google não encontrado')

    return access_token


def _get_sheets_service():
    token = _get_access_token()
    creds = Credentials(token=token)
    return build('sheets', 'v4', credentials=creds, cache_discovery=False)


def _get_drive_service():
    token = _get_access_token()
    creds = Credentials(token=token)
    return build('drive', 'v3', credentials=creds, cache_discovery=False)


def _find_spreadsheet():
    drive = _get_drive_service()
    results = drive.files().list(
        q=f"name='{SPREADSHEET_TITLE}' and mimeType='application/vnd.google-apps.spreadsheet' and trashed=false",
        spaces='drive',
        fields='files(id, name)'
    ).execute()
    files = results.get('files', [])
    return files[0]['id'] if files else None


def _create_spreadsheet():
    sheets = _get_sheets_service()
    spreadsheet = sheets.spreadsheets().create(body={
        'properties': {'title': SPREADSHEET_TITLE},
        'sheets': [{
            'properties': {'title': 'Procedimentos'},
            'data': [{
                'startRow': 0,
                'startColumn': 0,
                'rowData': [{
                    'values': [{'userEnteredValue': {'stringValue': h}} for h in SHEET_HEADERS]
                }]
            }]
        }]
    }).execute()
    spreadsheet_id = spreadsheet['spreadsheetId']

    sheets.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={
            'requests': [{
                'repeatCell': {
                    'range': {
                        'sheetId': 0,
                        'startRowIndex': 0,
                        'endRowIndex': 1,
                    },
                    'cell': {
                        'userEnteredFormat': {
                            'backgroundColor': {'red': 0.2, 'green': 0.4, 'blue': 0.7},
                            'textFormat': {'bold': True, 'foregroundColor': {'red': 1, 'green': 1, 'blue': 1}},
                            'horizontalAlignment': 'CENTER'
                        }
                    },
                    'fields': 'userEnteredFormat(backgroundColor,textFormat,horizontalAlignment)'
                }
            }, {
                'updateSheetProperties': {
                    'properties': {'sheetId': 0, 'gridProperties': {'frozenRowCount': 1}},
                    'fields': 'gridProperties.frozenRowCount'
                }
            }]
        }
    ).execute()

    print(f"✓ Planilha Google criada: {SPREADSHEET_TITLE} (ID: {spreadsheet_id})")
    return spreadsheet_id


def get_or_create_spreadsheet():
    spreadsheet_id = _find_spreadsheet()
    if not spreadsheet_id:
        spreadsheet_id = _create_spreadsheet()
    return spreadsheet_id


def _do_append_batch(procedures_data):
    try:
        spreadsheet_id = get_or_create_spreadsheet()
        sheets = _get_sheets_service()

        rows = []
        for proc in procedures_data:
            value = proc.get('value', 0)
            rows.append([
                proc.get('date', ''),
                proc.get('time', ''),
                proc.get('patient_name', ''),
                proc.get('procedure_name', ''),
                f"R$ {value:.2f}" if isinstance(value, (int, float)) else str(value),
                proc.get('consultation_type', ''),
                proc.get('status', 'Realizado'),
                proc.get('doctor_name', '')
            ])

        if rows:
            sheets.spreadsheets().values().append(
                spreadsheetId=spreadsheet_id,
                range='Procedimentos!A:H',
                valueInputOption='USER_ENTERED',
                insertDataOption='INSERT_ROWS',
                body={'values': rows}
            ).execute()

            print(f"✓ Google Sheets: {len(rows)} procedimentos adicionados em batch")
        return True
    except Exception as e:
        print(f"✗ Erro Google Sheets batch: {e}")
        return False


def append_procedures_batch(procedures_data):
    t = threading.Thread(target=_do_append_batch, args=(procedures_data,), daemon=True)
    t.start()


def append_procedure_row(patient_name, procedure_date, procedure_time, procedure_name, value, consultation_type, status, doctor_name):
    row_data = [{
        'date': procedure_date,
        'time': procedure_time,
        'patient_name': patient_name,
        'procedure_name': procedure_name,
        'value': value,
        'consultation_type': consultation_type,
        'status': status,
        'doctor_name': doctor_name
    }]
    append_procedures_batch(row_data)
