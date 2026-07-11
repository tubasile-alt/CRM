"""Shared helpers extracted from app.py without behavior changes."""

from models import Patient
from models import PatientDoctor
from models import db


NEW_PATIENT_CODE_START = 1001

def generate_next_patient_code(doctor_id):
    """Gera o próximo patient_code de forma segura contra concorrência.

    Regra de transição (FASE 1):
      - Se NÃO existir nenhum código >= 1001 para o médico => próximo = 1001.
      - Se já existir algum código >= 1001 => próximo = MAIOR_CODIGO + 1.

    A geração é protegida por LOCK de tabela no PostgreSQL para impedir que
    dois usuários simultâneos recebam o mesmo código (race condition). O lock
    é liberado automaticamente no commit/rollback da transação corrente.

    Deve ser chamada dentro de uma transação que será commitada pelo chamador.
    """
    if db.engine.dialect.name == 'postgresql':
        db.session.execute(
            db.text('LOCK TABLE patient_doctor IN SHARE ROW EXCLUSIVE MODE')
        )
    max_code = db.session.query(db.func.max(PatientDoctor.patient_code))\
        .filter(PatientDoctor.doctor_id == doctor_id).scalar() or 0
    return max(max_code + 1, NEW_PATIENT_CODE_START)

def normalize_patient_name(name):
    """Normaliza um nome de paciente para comparação:
    - remove espaços nas extremidades
    - colapsa espaços internos múltiplos em um único espaço
    - ignora maiúsculas/minúsculas (retorna em minúsculas)
    """
    import re
    if not name:
        return ''
    return re.sub(r'\s+', ' ', str(name).strip()).lower()

def find_possible_duplicate_patients(name, doctor_id=None, limit=8):
    """Procura pacientes com nome igual ou muito parecido ao informado.

    Retorna uma lista de dicts com dados básicos do paciente (incluindo o
    patient_code do médico, quando houver vínculo) para exibir no alerta de
    possível duplicidade. NÃO mescla nem altera nada — apenas detecta.
    """
    from difflib import SequenceMatcher

    target = normalize_patient_name(name)
    if not target:
        return []

    first_token = target.split(' ')[0]

    # Candidatos: nomes que contenham o primeiro token (reduz o conjunto),
    # comparação final feita em Python sobre o nome normalizado.
    candidates = Patient.query.filter(
        Patient.name.ilike(f'%{first_token}%')
    ).limit(200).all()

    results = []
    for cand in candidates:
        cand_norm = normalize_patient_name(cand.name)
        if not cand_norm:
            continue
        ratio = SequenceMatcher(None, target, cand_norm).ratio()
        if cand_norm == target or ratio >= 0.85:
            code = None
            if doctor_id:
                pd = PatientDoctor.query.filter_by(
                    patient_id=cand.id, doctor_id=doctor_id
                ).first()
                if pd:
                    code = pd.patient_code
            results.append({
                'id': cand.id,
                'name': cand.name,
                'patient_code': code,
                'phone': cand.phone,
                'birth_date': cand.birth_date,
                'cpf': cand.cpf,
                'city': cand.city,
                'exact': cand_norm == target,
                'similarity': round(ratio, 3),
            })

    # Mais parecidos primeiro
    results.sort(key=lambda r: (not r['exact'], -r['similarity']))
    return results[:limit]
