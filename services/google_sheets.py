import os
import threading
import requests as http_requests
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import re

SPREADSHEET_TITLE = "CRM Clínica Basile - Procedimentos"
SHEET_HEADERS = [
    "Nome Completo", "Procedimento", "Data do Procedimento", "Data do Retorno", "Telefone"
]


def format_phone_for_sheets(phone):
    """
    Formata telefone para o padrão Brasil (55 + número sem hífens).
    Exemplo: (16) 99994-1774 -> 5516999941774
    Exemplo: 16999941774 -> 5516999941774
    """
    if not phone:
        return ""
    
    # Remove tudo que não é número
    digits_only = re.sub(r'\D', '', str(phone).strip())
    
    # Se tem menos de 10 dígitos, retorna como está
    if len(digits_only) < 10:
        return digits_only
    
    # Se não começa com 55, adiciona
    if not digits_only.startswith('55'):
        digits_only = '55' + digits_only
    
    return digits_only


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
    actual_sheet_id = spreadsheet['sheets'][0]['properties']['sheetId']

    try:
        sheets.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={
                'requests': [{
                    'repeatCell': {
                        'range': {
                            'sheetId': actual_sheet_id,
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
                        'properties': {'sheetId': actual_sheet_id, 'gridProperties': {'frozenRowCount': 1}},
                        'fields': 'gridProperties.frozenRowCount'
                    }
                }]
            }
        ).execute()
    except Exception as fmt_err:
        print(f"⚠ Formatação da planilha falhou (não-crítico): {fmt_err}")

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
            rows.append([
                proc.get('patient_name', ''),
                proc.get('procedure_name', ''),
                proc.get('procedure_date', ''),
                proc.get('return_date', ''),
                format_phone_for_sheets(proc.get('phone', '')),
            ])

        if rows:
            sheets.spreadsheets().values().append(
                spreadsheetId=spreadsheet_id,
                range='Procedimentos!A:E',
                valueInputOption='USER_ENTERED',
                insertDataOption='INSERT_ROWS',
                body={'values': rows}
            ).execute()

            print(f"✓ Google Sheets: {len(rows)} procedimentos adicionados")
        return True
    except Exception as e:
        print(f"✗ Erro Google Sheets batch: {e}")
        return False


def append_procedures_batch(procedures_data):
    """Dispara em background a inserção de múltiplos procedimentos na planilha."""
    t = threading.Thread(target=_do_append_batch, args=(procedures_data,), daemon=True)
    t.start()


def _do_append_transplant(data):
    try:
        spreadsheet_id = get_or_create_spreadsheet()
        sheets = _get_sheets_service()
        sheet_name = 'Transplante Capilar'
        
        # Garantir que a aba existe
        sheet_metadata = sheets.get(spreadsheetId=spreadsheet_id).execute()
        sheets_list = sheet_metadata.get('sheets', [])
        exists = any(s.get('properties', {}).get('title') == sheet_name for s in sheets_list)
        
        if not exists:
            sheets.batchUpdate(spreadsheetId=spreadsheet_id, body={
                'requests': [{'addSheet': {'properties': {'title': sheet_name}}}]
            }).execute()
            sheets.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=f'\'{sheet_name}\'!A1',
                valueInputOption='USER_ENTERED',
                body={'values': [["Nome do Paciente", "Celular", "Data da Consulta", "Status", "Data da Cirurgia"]]}
            ).execute()

        # Buscar dados existentes para evitar duplicados
        result = sheets.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=f'\'{sheet_name}\'!A:A'
        ).execute()
        existing_names = {row[0].strip().lower() for row in result.get('values', []) if row}

        rows_to_append = []
        for item in data:
            name = item.get('patient_name', '').strip()
            if name.lower() in existing_names:
                continue
                
            phone = format_phone_for_sheets(item.get('phone', ''))
            status = item.get('status', 'pendente')
            surgery_date = item.get('surgery_date', '')
            
            rows_to_append.append([
                name,
                phone,
                item.get('consult_date', ''),
                status,
                surgery_date
            ])

        if rows_to_append:
            sheets.spreadsheets().values().append(
                spreadsheetId=spreadsheet_id,
                range=f'\'{sheet_name}\'!A:E',
                valueInputOption='USER_ENTERED',
                insertDataOption='INSERT_ROWS',
                body={'values': rows_to_append}
            ).execute()
        return True
    except Exception as e:
        print(f"✗ Erro Google Sheets Transplante: {e}")
        return False

def append_transplant_data(data):
    t = threading.Thread(target=_do_append_transplant, args=(data,), daemon=True)
    t.start()


# ──────────────────────────────────────────────────────────────────────────────
# ABA BOTOX – espelho reconciliado do banco
# ──────────────────────────────────────────────────────────────────────────────
BOTOX_SPREADSHEET_ID = '1IUNWhBRzt5u6_ttfzjfTKckhSMOMx1l_s7uGnIom66o'
BOTOX_SHEET_NAME     = 'Botox'
BOTOX_HEADERS = [
    'execution_ids', 'Paciente', 'Celular', 'Data Realizado',
    'Data Follow-up (5 meses)', 'Status D0', 'Tentativas D0',
    'Último erro D0', 'Enviada D0', 'Status 5m', 'Tentativas 5m',
    'Último erro 5m', 'Enviada 5m',
]


def _ensure_botox_sheet(headers_req, base, access_token):
    """Garante que a aba Botox existe e tem cabeçalho. Retorna True se ok."""
    meta = headers_req.get(f'{base}?fields=sheets.properties.title', timeout=10)
    if meta.status_code != 200:
        return False
    titles = [s['properties']['title'] for s in meta.json().get('sheets', [])]
    if BOTOX_SHEET_NAME not in titles:
        headers_req.post(f'{base}:batchUpdate', timeout=10, json={
            'requests': [{'addSheet': {'properties': {'title': BOTOX_SHEET_NAME}}}]
        })
        headers_req.put(
            f'{base}/values/{BOTOX_SHEET_NAME}!A1',
            timeout=10,
            params={'valueInputOption': 'USER_ENTERED'},
            json={'values': [BOTOX_HEADERS]}
        )
    return True


def write_botox_sheet(values_matrix):
    """Reescreve a aba Botox inteira, preservando o conteúdo se o PUT falhar."""
    try:
        import requests as req
        token = _get_access_token()
        h = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
        base = f'https://sheets.googleapis.com/v4/spreadsheets/{BOTOX_SPREADSHEET_ID}'

        class _S:
            def get(self, *a, **kw):  return req.get(*a, headers=h, **kw)
            def post(self, *a, **kw): return req.post(*a, headers=h, **kw)
            def put(self, *a, **kw):  return req.put(*a, headers=h, **kw)
        if not _ensure_botox_sheet(_S(), base, token):
            return False, 'não foi possível garantir a aba Botox'

        resp = req.put(
            f'{base}/values/{BOTOX_SHEET_NAME}!A1',
            headers=h,
            timeout=60,
            params={'valueInputOption': 'USER_ENTERED'},
            json={'values': values_matrix},
        )
        if resp.status_code not in (200, 201):
            return False, f'PUT falhou: {resp.status_code} {resp.text[:200]}'

        first_stale_row = len(values_matrix) + 1
        req.post(
            f'{base}/values/{BOTOX_SHEET_NAME}!A{first_stale_row}:M100000:clear',
            headers=h,
            timeout=30,
        )
        return True, f'{len(values_matrix) - 1} linhas sincronizadas'
    except Exception as e:
        return False, f'erro inesperado: {e}'
