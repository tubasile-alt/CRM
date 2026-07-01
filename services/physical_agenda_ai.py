"""Transcrição multimodal de agenda física, sem persistência local."""
import base64
import json
import logging
import re

from flask import current_app


logger = logging.getLogger(__name__)

ITEM_SCHEMA = {
    'type': 'object',
    'additionalProperties': False,
    'properties': {
        'time': {'type': ['string', 'null']},
        'patient_name': {'type': ['string', 'null']},
        'phone': {'type': ['string', 'null']},
        'appointment_type': {'type': ['string', 'null']},
        'procedure': {'type': ['string', 'null']},
        'notes': {'type': ['string', 'null']},
        'confidence': {'type': 'number', 'minimum': 0, 'maximum': 1},
        'raw_text': {'type': ['string', 'null']},
    },
    'required': [
        'time',
        'patient_name',
        'phone',
        'appointment_type',
        'procedure',
        'notes',
        'confidence',
        'raw_text',
    ],
}

RESPONSE_SCHEMA = {
    'type': 'object',
    'additionalProperties': False,
    'properties': {
        'items': {'type': 'array', 'items': ITEM_SCHEMA},
        'warnings': {'type': 'array', 'items': {'type': 'string'}},
    },
    'required': ['items', 'warnings'],
}

SYSTEM_PROMPT = """Você é um assistente de transcrição de agenda médica manuscrita.
Extraia somente os compromissos visíveis na imagem da agenda física.

Regras obrigatórias:
- Não invente dados. Quando algo estiver ilegível ou ausente, use null e reduza confidence.
- Preserve horários no formato HH:MM. Não deduza horário sem evidência visual.
- Preserve em raw_text a linha original interpretada, sem corrigir silenciosamente o conteúdo.
- Normalize telefones para somente dígitos quando houver segurança; preserve a leitura original em raw_text.
- Interprete abreviações apenas quando o contexto sustentar: ret = retorno; botox = Botox;
  IC = indicação ou consulta inicial; 1º pós e 1 sem = retorno pós-procedimento.
- Use appointment_type para a categoria da consulta e procedure para o procedimento citado.
- confidence deve ficar entre 0 e 1 e refletir a confiança do item completo.
- Não inclua campos fora do schema e não inclua explicações fora do JSON.
"""


class PhysicalAgendaAIError(RuntimeError):
    """Erro seguro para apresentação ao usuário."""


def _clean_text(value, max_length):
    if value is None:
        return None
    cleaned = ' '.join(str(value).split()).strip()
    return cleaned[:max_length] or None


def _normalize_item(item):
    if not isinstance(item, dict):
        return None

    raw_time = _clean_text(item.get('time'), 5)
    time_value = raw_time if raw_time and re.fullmatch(r'(?:[01]\d|2[0-3]):[0-5]\d', raw_time) else None

    raw_phone = _clean_text(item.get('phone'), 40)
    phone_digits = re.sub(r'\D', '', raw_phone or '')
    phone_value = phone_digits[:15] or None

    try:
        confidence = float(item.get('confidence', 0))
    except (TypeError, ValueError):
        confidence = 0.0
    confidence = round(max(0.0, min(1.0, confidence)), 2)

    return {
        'time': time_value,
        'patient_name': _clean_text(item.get('patient_name'), 160),
        'phone': phone_value,
        'appointment_type': _clean_text(item.get('appointment_type'), 80),
        'procedure': _clean_text(item.get('procedure'), 120),
        'notes': _clean_text(item.get('notes'), 500),
        'confidence': confidence,
        'raw_text': _clean_text(item.get('raw_text'), 500),
    }


def _normalize_result(payload):
    if not isinstance(payload, dict):
        raise PhysicalAgendaAIError('A IA retornou uma resposta em formato inválido.')

    items = []
    for raw_item in payload.get('items') or []:
        item = _normalize_item(raw_item)
        if item is not None:
            items.append(item)

    warnings = [
        warning
        for warning in (_clean_text(value, 300) for value in (payload.get('warnings') or []))
        if warning
    ][:20]
    if not items and not warnings:
        warnings.append('Nenhum compromisso legível foi identificado na imagem.')

    return {'items': items[:100], 'warnings': warnings}


def analyze_physical_agenda_image(image_bytes, mime_type, agenda_date, doctor_name):
    """Envia uma imagem em memória para transcrição e retorna dados normalizados."""
    api_key = current_app.config.get('OPENAI_API_KEY')
    model = current_app.config.get('OPENAI_VISION_MODEL') or 'gpt-4.1-mini'
    if not api_key:
        raise PhysicalAgendaAIError('OPENAI_API_KEY não configurada.')

    image_data = base64.b64encode(image_bytes).decode('ascii')
    context_prompt = (
        f'Data selecionada: {agenda_date}. Médico responsável: {doctor_name}. '
        'Use esses dados apenas como contexto; não os trate como texto visível na imagem.'
    )

    try:
        from openai import APIConnectionError, APITimeoutError, AuthenticationError, OpenAI, RateLimitError
    except ImportError as exc:
        logger.error('SDK da OpenAI indisponível para análise de agenda física.')
        raise PhysicalAgendaAIError('Integração com a OpenAI indisponível no servidor.') from exc

    try:
        client = OpenAI(api_key=api_key, timeout=60.0)
        response = client.responses.create(
            model=model,
            store=False,
            max_output_tokens=4000,
            input=[{
                'role': 'user',
                'content': [
                    {'type': 'input_text', 'text': f'{SYSTEM_PROMPT}\n\n{context_prompt}'},
                    {
                        'type': 'input_image',
                        'image_url': f'data:{mime_type};base64,{image_data}',
                        'detail': 'high',
                    },
                ],
            }],
            text={
                'format': {
                    'type': 'json_schema',
                    'name': 'physical_agenda_transcription',
                    'strict': True,
                    'schema': RESPONSE_SCHEMA,
                },
            },
        )
        if not response.output_text:
            raise PhysicalAgendaAIError('A IA não retornou conteúdo para conferência.')
        return _normalize_result(json.loads(response.output_text))
    except AuthenticationError as exc:
        logger.warning('Falha de autenticação OpenAI ao analisar agenda física.')
        raise PhysicalAgendaAIError('A chave da OpenAI é inválida ou não está autorizada.') from exc
    except RateLimitError as exc:
        logger.warning('Limite da OpenAI atingido ao analisar agenda física.')
        raise PhysicalAgendaAIError('A OpenAI está temporariamente ocupada. Tente novamente em instantes.') from exc
    except (APIConnectionError, APITimeoutError) as exc:
        logger.warning('Falha de conexão com a OpenAI ao analisar agenda física.')
        raise PhysicalAgendaAIError('Não foi possível conectar à OpenAI. Tente novamente.') from exc
    except json.JSONDecodeError as exc:
        logger.warning('Resposta JSON inválida recebida na análise de agenda física.')
        raise PhysicalAgendaAIError('A IA retornou dados inválidos. Tente analisar novamente.') from exc
    except PhysicalAgendaAIError:
        raise
    except Exception as exc:
        logger.error('Erro técnico na análise de agenda física: %s', type(exc).__name__)
        raise PhysicalAgendaAIError('Não foi possível analisar a imagem da agenda.') from exc
