"""Resumo compacto do prontuário usando IA com cache por hash de conteúdo."""

import hashlib
import json
import logging
import re
from collections import OrderedDict
from datetime import date, datetime

from flask import current_app

from models import (
    Appointment,
    CosmeticProcedurePlan,
    Evolution,
    HairTransplant,
    Note,
    Patient,
    Prescription,
    TransplantSurgeryRecord,
    db,
)
from services.clinic_time import clinic_today


logger = logging.getLogger(__name__)

SUMMARY_RESPONSE_SCHEMA = {
    'type': 'object',
    'additionalProperties': False,
    'properties': {
        'summary': {'type': 'string'},
        'alerts': {'type': 'array', 'items': {'type': 'string'}},
        'pending': {'type': 'array', 'items': {'type': 'string'}},
    },
    'required': ['summary', 'alerts', 'pending'],
}

SYSTEM_PROMPT = """Você resume prontuários médicos para revisão clínica rápida.
Use apenas os dados fornecidos. Não invente informações.
Omitir campos vazios. Não mencionar dados administrativos.
q=queixa, a=anamnese/exame, dx=diagnóstico, c=conduta.
Responder em português do Brasil, objetivo, com no máximo 1200 caracteres no total.
summary deve trazer o quadro atual e condutas recentes em texto corrido curto.
alerts deve conter apenas riscos clínicos importantes.
pending deve conter apenas pendências práticas de seguimento.
"""


class ProntuarioSummaryAIError(RuntimeError):
    """Erro seguro para apresentar ao usuário."""


def _clean_text(value, max_length=700, patient_name=None):
    if value is None:
        return None

    text = ' '.join(str(value).split()).strip()
    if not text:
        return None

    text = re.sub(r'[\w.+-]+@[\w-]+(?:\.[\w-]+)+', '[email]', text)
    text = re.sub(r'\b(?:\+?55)?\d{10,13}\b', '[telefone]', text)
    text = re.sub(r'\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b', '[cpf]', text)

    if patient_name:
        name = ' '.join(str(patient_name).split()).strip()
        if len(name) >= 4:
            text = re.sub(re.escape(name), '[paciente]', text, flags=re.IGNORECASE)

    return text[:max_length] or None


def _drop_empty(value):
    if isinstance(value, dict):
        cleaned = {
            key: _drop_empty(item)
            for key, item in value.items()
        }
        return {
            key: item
            for key, item in cleaned.items()
            if item not in (None, '', [], {})
        }
    if isinstance(value, list):
        return [
            item for item in (_drop_empty(item) for item in value)
            if item not in (None, '', [], {})
        ]
    return value


def _date_iso(value):
    if not value:
        return None
    if isinstance(value, datetime):
        return value.strftime('%Y-%m-%d')
    if isinstance(value, date):
        return value.isoformat()
    return None


def _datetime_key(value):
    if isinstance(value, datetime):
        return value
    if isinstance(value, date):
        return datetime.combine(value, datetime.min.time())
    return datetime.min


def _patient_age(patient):
    if not patient.birth_date:
        return None
    try:
        today = clinic_today()
        return today.year - patient.birth_date.year - (
            (today.month, today.day) < (patient.birth_date.month, patient.birth_date.day)
        )
    except Exception:
        return None


def _patient_context(patient):
    data = {
        'idade': _patient_age(patient),
        'alergias': _clean_text(patient.allergies, 300, patient.name),
        'atencao': _clean_text(patient.attention_note, 300, patient.name),
        'fumante': _clean_text(patient.smoker, 40, patient.name),
        'sangue': _clean_text(patient.blood_type, 10, patient.name),
    }
    if patient.weight and patient.height and patient.height > 0:
        height_m = patient.height / 100
        data['imc'] = round(patient.weight / (height_m * height_m), 1)
    return _drop_empty(data)


def _appointment_map(notes):
    appointment_ids = sorted({note.appointment_id for note in notes if note.appointment_id})
    if not appointment_ids:
        return {}
    appointments = Appointment.query.filter(Appointment.id.in_(appointment_ids)).all()
    return {appointment.id: appointment for appointment in appointments}


def _note_group_key(note):
    if note.appointment_id:
        return f'apt:{note.appointment_id}'
    created = note.created_at or datetime.min
    return f'note:{note.doctor_id}:{created.strftime("%Y%m%d%H%M")}'


def _recent_consultations(patient_id, patient_name, limit=5):
    notes = (
        Note.query
        .filter_by(patient_id=patient_id)
        .order_by(Note.created_at.desc(), Note.id.desc())
        .limit(80)
        .all()
    )
    appointments = _appointment_map(notes)
    groups = OrderedDict()
    note_keys = {
        'queixa': 'q',
        'anamnese': 'a',
        'diagnostico': 'dx',
        'conduta': 'c',
        'planejamento': 'plan',
        'transplante': 'tx',
    }

    for note in notes:
        key = _note_group_key(note)
        appointment = appointments.get(note.appointment_id)
        if appointment:
            dt = appointment.consultation_date or appointment.start_time
        else:
            dt = note.created_at
        if key not in groups:
            groups[key] = {
                'dt': dt,
                'data': _date_iso(dt),
                'tipo': _clean_text(
                    (appointment.appointment_type if appointment else note.category) or 'consulta',
                    80,
                    patient_name,
                ),
                'notas': {},
                'procedimentos': [],
            }

        short_key = note_keys.get((note.note_type or '').strip().lower())
        content = _clean_text(note.content, 700, patient_name)
        if short_key and content and short_key not in groups[key]['notas']:
            groups[key]['notas'][short_key] = content

        surgical_planning = _clean_text(note.surgical_planning, 500, patient_name)
        if surgical_planning:
            groups[key]['notas'].setdefault('cir', surgical_planning)

        for plan in note.cosmetic_plans[:4]:
            plan_name = _clean_text(plan.procedure_name or plan.name, 80, patient_name)
            if plan_name:
                groups[key]['procedimentos'].append(plan_name)

    ordered_groups = sorted(
        groups.values(),
        key=lambda item: _datetime_key(item.get('dt')),
        reverse=True,
    )
    result = []
    for group in ordered_groups[:limit]:
        group.pop('dt', None)
        group['procedimentos'] = list(dict.fromkeys(group.get('procedimentos') or []))[:4]
        cleaned = _drop_empty(group)
        if cleaned:
            result.append(cleaned)
    return result


def _recent_evolutions(patient_id, patient_name, limit=5):
    rows = (
        Evolution.query
        .filter_by(patient_id=patient_id)
        .order_by(Evolution.evolution_date.desc(), Evolution.id.desc())
        .limit(limit)
        .all()
    )
    return _drop_empty([
        {
            'data': _date_iso(row.evolution_date),
            'texto': _clean_text(row.content, 500, patient_name),
        }
        for row in rows
    ])


def _recent_plans(patient_id, patient_name, limit=6):
    plans = (
        CosmeticProcedurePlan.query
        .join(Note)
        .filter(Note.patient_id == patient_id)
        .order_by(CosmeticProcedurePlan.created_at.desc(), CosmeticProcedurePlan.id.desc())
        .limit(limit)
        .all()
    )
    return _drop_empty([
        {
            'nome': _clean_text(plan.procedure_name or plan.name, 80, patient_name),
            'status': _clean_text(plan.status, 30, patient_name),
            'realizado': bool(plan.was_performed),
            'obs': _clean_text(plan.observations, 240, patient_name),
        }
        for plan in plans
    ])


def _recent_prescriptions(patient_id, patient_name, limit=2):
    prescriptions = (
        Prescription.query
        .filter_by(patient_id=patient_id)
        .order_by(Prescription.created_at.desc(), Prescription.id.desc())
        .limit(limit)
        .all()
    )
    result = []
    for prescription in prescriptions:
        meds = []
        for med in (prescription.medications_oral or [])[:4]:
            if isinstance(med, dict):
                raw_name = med.get('medication') or med.get('name')
            else:
                raw_name = med
            name = _clean_text(raw_name, 80, patient_name)
            if name:
                meds.append(name)
        for med in (prescription.medications_topical or [])[:4]:
            if isinstance(med, dict):
                raw_name = med.get('medication') or med.get('name')
            else:
                raw_name = med
            name = _clean_text(raw_name, 80, patient_name)
            if name:
                meds.append(name)
        result.append({
            'data': _date_iso(prescription.created_at),
            'meds': list(dict.fromkeys(meds))[:6],
            'resumo': _clean_text(prescription.summary, 240, patient_name),
        })
    return _drop_empty(result)


def _recent_transplants(patient_id, patient_name, limit=3):
    records = (
        TransplantSurgeryRecord.query
        .filter_by(patient_id=patient_id)
        .order_by(TransplantSurgeryRecord.surgery_date.desc(), TransplantSurgeryRecord.id.desc())
        .limit(limit)
        .all()
    )
    hair = (
        HairTransplant.query
        .join(Note)
        .filter(Note.patient_id == patient_id)
        .order_by(HairTransplant.created_at.desc(), HairTransplant.id.desc())
        .limit(limit)
        .all()
    )
    payload = [
        {
            'data': _date_iso(row.surgery_date),
            'tipo': _clean_text(row.surgery_type, 80, patient_name),
            'dados': _clean_text(row.surgical_data, 300, patient_name),
            'obs': _clean_text(row.observations, 300, patient_name),
        }
        for row in records
    ]
    payload.extend([
        {
            'data': _date_iso(row.created_at),
            'norwood': _clean_text(row.norwood_classification, 20, patient_name),
            'plano': _clean_text(row.surgical_planning, 300, patient_name),
            'conduta': _clean_text(row.clinical_conduct, 300, patient_name),
        }
        for row in hair
    ])
    return _drop_empty(payload[:limit])


def build_prontuario_summary_source(patient_id):
    patient = db.session.get(Patient, patient_id)
    if not patient:
        raise ValueError('Paciente não encontrado.')

    payload = _drop_empty({
        'schema': 'prontuario_resumo_v1',
        'paciente': _patient_context(patient),
        'consultas': _recent_consultations(patient_id, patient.name),
        'evolucoes': _recent_evolutions(patient_id, patient.name),
        'planos': _recent_plans(patient_id, patient.name),
        'prescricoes': _recent_prescriptions(patient_id, patient.name),
        'transplante': _recent_transplants(patient_id, patient.name),
    })

    max_chars = max(2000, int(current_app.config.get('PRONTUARIO_SUMMARY_SOURCE_MAX_CHARS', 9000)))
    while len(json.dumps(payload, ensure_ascii=False, sort_keys=True)) > max_chars:
        if len(payload.get('consultas') or []) > 3:
            payload['consultas'].pop()
        elif len(payload.get('evolucoes') or []) > 2:
            payload['evolucoes'].pop()
        elif len(payload.get('planos') or []) > 3:
            payload['planos'].pop()
        elif len(payload.get('prescricoes') or []) > 1:
            payload['prescricoes'].pop()
        else:
            break

    source_hash = hashlib.sha256(
        json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode('utf-8')
    ).hexdigest()

    has_source_content = any(payload.get(key) for key in (
        'consultas',
        'evolucoes',
        'planos',
        'prescricoes',
        'transplante',
    )) or bool((payload.get('paciente') or {}).keys() - {'idade'})

    return payload, source_hash, has_source_content


def _normalize_ai_result(payload):
    if not isinstance(payload, dict):
        raise ProntuarioSummaryAIError('A IA retornou uma resposta em formato inválido.')

    summary = _clean_text(payload.get('summary'), 1400)
    alerts = [
        item for item in (_clean_text(value, 180) for value in (payload.get('alerts') or []))
        if item
    ][:4]
    pending = [
        item for item in (_clean_text(value, 180) for value in (payload.get('pending') or []))
        if item
    ][:4]

    if not summary:
        raise ProntuarioSummaryAIError('A IA não conseguiu gerar um resumo útil.')

    return {
        'summary': summary,
        'alerts': alerts,
        'pending': pending,
    }


def generate_prontuario_summary(source_payload):
    api_key = current_app.config.get('OPENAI_API_KEY')
    model = current_app.config.get('OPENAI_SUMMARY_MODEL') or current_app.config.get('OPENAI_VISION_MODEL')
    if not api_key:
        raise ProntuarioSummaryAIError('OPENAI_API_KEY não configurada.')
    if not model:
        raise ProntuarioSummaryAIError('Modelo de resumo IA não configurado.')

    try:
        from openai import APIConnectionError, APITimeoutError, AuthenticationError, OpenAI, RateLimitError
    except ImportError as exc:
        logger.error('SDK da OpenAI indisponível para resumo do prontuário.')
        raise ProntuarioSummaryAIError('Integração com a OpenAI indisponível no servidor.') from exc

    try:
        client = OpenAI(api_key=api_key, timeout=45.0)
        response = client.responses.create(
            model=model,
            store=False,
            max_output_tokens=700,
            input=[{
                'role': 'user',
                'content': [{
                    'type': 'input_text',
                    'text': f'{SYSTEM_PROMPT}\n\nDados compactos do prontuário:\n{json.dumps(source_payload, ensure_ascii=False, separators=(",", ":"))}',
                }],
            }],
            text={
                'format': {
                    'type': 'json_schema',
                    'name': 'prontuario_ai_summary',
                    'strict': True,
                    'schema': SUMMARY_RESPONSE_SCHEMA,
                },
            },
        )
        if not response.output_text:
            raise ProntuarioSummaryAIError('A IA não retornou conteúdo.')
        return _normalize_ai_result(json.loads(response.output_text)), model
    except AuthenticationError as exc:
        logger.warning('Falha de autenticação OpenAI ao resumir prontuário.')
        raise ProntuarioSummaryAIError('A chave da OpenAI é inválida ou não está autorizada.') from exc
    except RateLimitError as exc:
        logger.warning('Limite da OpenAI atingido ao resumir prontuário.')
        raise ProntuarioSummaryAIError('A OpenAI está temporariamente ocupada. Tente novamente em instantes.') from exc
    except (APIConnectionError, APITimeoutError) as exc:
        logger.warning('Falha de conexão com a OpenAI ao resumir prontuário.')
        raise ProntuarioSummaryAIError('Não foi possível conectar à OpenAI. Tente novamente.') from exc
    except json.JSONDecodeError as exc:
        logger.warning('Resposta JSON inválida recebida no resumo do prontuário.')
        raise ProntuarioSummaryAIError('A IA retornou dados inválidos. Tente gerar novamente.') from exc
    except ProntuarioSummaryAIError:
        raise
    except Exception as exc:
        logger.error('Erro técnico no resumo do prontuário: %s', type(exc).__name__)
        raise ProntuarioSummaryAIError('Não foi possível gerar o resumo do prontuário.') from exc
