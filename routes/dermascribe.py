import re
from flask import Blueprint, render_template, request, jsonify, send_file, make_response
from flask_login import login_required, current_user
from models import db, Medication, MedicationUsage, Prescription, Patient
from services.openai_service import suggest_medications
from sqlalchemy.orm import joinedload
from weasyprint import HTML
import io
import csv
from datetime import datetime

dermascribe_bp = Blueprint('dermascribe', __name__, url_prefix='/dermascribe')

CITE_RE = re.compile(r"\[cite:\s*\d+\]", re.IGNORECASE)

DEFAULT_PRINT_TEMPLATE = "dermascribe/print.html"
PRINT_TEMPLATE_MAP = {
    "dermascribe": "dermascribe/print.html",
    "standard": "dermascribe/print.html",
    "antibiotico": "dermascribe/print_basile_vias.html",
    "isotretinoina": "dermascribe/print_basile_vias.html",
}


def _resolve_print_template(prescription):
    ptype = getattr(prescription, 'prescription_type', None) or 'standard'
    return PRINT_TEMPLATE_MAP.get(ptype, DEFAULT_PRINT_TEMPLATE)


def strip_citations(value: str) -> str:
    if not value:
        return value
    cleaned = CITE_RE.sub("", value)
    cleaned = re.sub(r"\s{2,}", " ", cleaned)
    cleaned = re.sub(r"\s+([,.;:])", r"\1", cleaned)
    return cleaned.strip()

@dermascribe_bp.route('/')
@login_required
def index():
    patient_name = request.args.get('patient', '')
    patient_id = request.args.get('patient_id', '')
    return render_template('dermascribe/index.html', patient_name=patient_name, patient_id=patient_id)

@dermascribe_bp.route('/api/suggest-medications', methods=['POST'])
@login_required
def api_suggest_medications():
    data = request.get_json()
    partial_input = data.get('partial_input', '')
    
    if len(partial_input) < 2:
        return jsonify({'suggestions': []})
    
    db_suggestions = Medication.query.filter(
        Medication.name.ilike(f'%{partial_input}%')
    ).limit(5).all()
    
    if db_suggestions:
        suggestions = [med.to_dict() for med in db_suggestions]
    else:
        suggestions = suggest_medications(partial_input)
    
    return jsonify({'suggestions': suggestions})

@dermascribe_bp.route('/api/save-medication', methods=['POST'])
@login_required
def api_save_medication():
    data = request.get_json()

    medication_name = data.get('medication', '')
    medication_type = data.get('type', 'topical')
    instructions = data.get('instructions', '')
    categoria = data.get('categoria', None)
    indicacoes = data.get('indicacoes', None)
    etiqueta_revisada = data.get('etiqueta_revisada', False)

    if not medication_name:
        return jsonify({'status': 'error', 'message': 'Nome do medicamento é obrigatório'})

    existing = Medication.query.filter(
        Medication.name.ilike(medication_name)
    ).first()

    if existing:
        # Se veio categoria/indicações, atualizar o medicamento existente
        updated = False
        if categoria and (not existing.categoria or not existing.etiqueta_revisada):
            existing.categoria = categoria
            updated = True
        if indicacoes:
            existing.indicacoes = indicacoes
            updated = True
        if etiqueta_revisada:
            existing.etiqueta_revisada = True
            updated = True
        if updated:
            db.session.commit()
        return jsonify({'status': 'exists', 'message': 'Medicamento já existe no banco', 'id': existing.id, 'updated': updated})

    new_medication = Medication(
        name=medication_name,
        type=medication_type,
        instructions=instructions,
        categoria=categoria,
        indicacoes=indicacoes,
        etiqueta_revisada=bool(etiqueta_revisada)
    )

    db.session.add(new_medication)
    db.session.commit()

    return jsonify({'status': 'success', 'message': 'Medicamento salvo com sucesso', 'id': new_medication.id})


@dermascribe_bp.route('/api/taxonomia', methods=['GET'])
@login_required
def api_taxonomia():
    """Retorna categorias e indicações existentes no banco."""
    from sqlalchemy import func

    cats = db.session.query(Medication.categoria).filter(
        Medication.categoria.isnot(None)
    ).distinct().order_by(Medication.categoria).all()
    categorias = [c[0] for c in cats if c[0]]

    # Indicações: extrair de JSON arrays
    meds_with_ind = Medication.query.filter(Medication.indicacoes.isnot(None)).all()
    indicacoes_set = set()
    for m in meds_with_ind:
        if isinstance(m.indicacoes, list):
            for item in m.indicacoes:
                if item:
                    indicacoes_set.add(item)
        elif isinstance(m.indicacoes, str):
            indicacoes_set.add(m.indicacoes)

    return jsonify({
        'categorias': sorted(categorias),
        'indicacoes': sorted(indicacoes_set)
    })


@dermascribe_bp.route('/api/descobrir', methods=['GET'])
@login_required
def api_descobrir():
    """Descoberta de medicamentos por categoria e/ou indicação."""
    from sqlalchemy import func
    categoria = request.args.get('categoria', '').strip().lower()
    indicacao = request.args.get('indicacao', '').strip().lower()

    q = db.session.query(Medication, func.count(MedicationUsage.id).label('use_count'))\
        .outerjoin(MedicationUsage)\
        .group_by(Medication.id)

    if categoria:
        q = q.filter(func.lower(Medication.categoria) == categoria)

    meds = q.order_by(func.count(MedicationUsage.id).desc()).all()

    results = []
    for med, count in meds:
        inds = []
        if isinstance(med.indicacoes, list):
            inds = med.indicacoes
        elif isinstance(med.indicacoes, str):
            inds = [med.indicacoes]

        if indicacao:
            if not any(indicacao in (i or '').lower() for i in inds):
                continue

        results.append({
            'id': med.id,
            'name': med.name,
            'brand': med.brand,
            'type': med.type,
            'categoria': med.categoria,
            'indicacoes': inds,
            'use_count': count
        })

    sem_etiqueta = Medication.query.filter(
        (Medication.etiqueta_revisada == False) | (Medication.etiqueta_revisada.is_(None))
    ).count()

    return jsonify({
        'medicamentos': results,
        'sem_etiqueta': sem_etiqueta
    })

@dermascribe_bp.route('/api/track-prescription', methods=['POST'])
@login_required
def api_track_prescription():
    data = request.get_json()
    medications = data.get('medications', [])
    
    for med in medications:
        med_name = med.get('medication', '')
        existing = Medication.query.filter(
            Medication.name.ilike(med_name)
        ).first()
        
        if existing:
            usage = MedicationUsage(medication_id=existing.id)
            db.session.add(usage)
    
    db.session.commit()
    return jsonify({'status': 'success'})

@dermascribe_bp.route('/api/analytics/top-medications')
@login_required
def api_top_medications():
    top_meds = Medication.get_top_prescribed(limit=10)
    
    result = []
    for med, count in top_meds:
        result.append({
            'id': med.id,
            'name': med.name,
            'type': med.type,
            'count': count
        })
    
    return jsonify({'medications': result})

@dermascribe_bp.route('/api/export-medications-excel')
@login_required
def api_export_excel():
    medications = Medication.query.order_by(Medication.name).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow(['Nome', 'Tipo', 'Marca', 'Instruções', 'Criado em'])
    
    for med in medications:
        writer.writerow([
            med.name,
            'Tópico' if med.type == 'topical' else 'Oral',
            med.brand or '',
            med.instructions or '',
            med.created_at.strftime('%d/%m/%Y') if med.created_at else ''
        ])
    
    output.seek(0)
    
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8-sig')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'medicamentos_{datetime.now().strftime("%Y%m%d")}.csv'
    )

@dermascribe_bp.route('/api/save-prescription', methods=['POST'])
@login_required
def api_save_prescription():
    data = request.get_json()
    
    patient_id = data.get('patient_id')
    patient_name = data.get('patient_name', '')
    oral_medications = data.get('oral', [])
    topical_medications = data.get('topical', [])
    
    if not patient_id:
        return jsonify({'status': 'error', 'message': 'ID do paciente é obrigatório'})
    
    # Limpeza de citações
    for med in oral_medications:
        med["medication"] = strip_citations(med.get("medication", ""))
        med["instructions"] = strip_citations(med.get("instructions", ""))

    for med in topical_medications:
        med["medication"] = strip_citations(med.get("medication", ""))
        med["instructions"] = strip_citations(med.get("instructions", ""))
    
    patient = Patient.query.get(patient_id)
    if not patient:
        return jsonify({'status': 'error', 'message': 'Paciente não encontrado'})
    
    VALID_PRESCRIPTION_TYPES = {'dermascribe', 'standard', 'antibiotico', 'isotretinoina'}
    ptype = data.get('prescription_type', 'dermascribe') or 'dermascribe'
    if ptype not in VALID_PRESCRIPTION_TYPES:
        ptype = 'dermascribe'

    prescription = Prescription(
        patient_id=patient_id,
        doctor_id=current_user.id,
        medications_oral=oral_medications,
        medications_topical=topical_medications,
        prescription_type=ptype
    )
    
    db.session.add(prescription)
    
    all_medications = oral_medications + topical_medications
    new_medications = []
    for med in all_medications:
        med_name = med.get('medication', '')
        existing = Medication.query.filter(
            Medication.name.ilike(med_name)
        ).first()

        if existing:
            usage = MedicationUsage(medication_id=existing.id)
            db.session.add(usage)
        else:
            new_med = Medication(
                name=med_name,
                type=med.get('type', 'topical'),
                instructions=med.get('instructions', '')
            )
            db.session.add(new_med)
            db.session.flush()
            usage = MedicationUsage(medication_id=new_med.id)
            db.session.add(usage)
            new_medications.append({
                'name': new_med.name,
                'type': new_med.type,
                'instructions': new_med.instructions or ''
            })

    db.session.commit()

    return jsonify({
        'status': 'success',
        'message': 'Receita salva com sucesso',
        'prescription_id': prescription.id,
        'new_medications': new_medications
    })

@dermascribe_bp.route('/api/patient/<int:patient_id>/prescriptions')
@login_required
def api_patient_prescriptions(patient_id):
    prescriptions = Prescription.query.filter_by(patient_id=patient_id).order_by(Prescription.created_at.desc()).all()
    
    result = []
    for p in prescriptions:
        result.append({
            'id': p.id,
            'doctor': p.doctor.name if p.doctor else 'Desconhecido',
            'oral': p.medications_oral or [],
            'topical': p.medications_topical or [],
            'created_at': p.created_at.strftime('%d/%m/%Y %H:%M') if p.created_at else ''
        })
    
    return jsonify({'prescriptions': result})

@dermascribe_bp.route('/prescription/<int:prescription_id>/print')
@login_required
def print_prescription(prescription_id):
    prescription = (
        Prescription.query
        .options(joinedload(Prescription.doctor))
        .get_or_404(prescription_id)
    )

    patient = Patient.query.get_or_404(prescription.patient_id)

    if not getattr(prescription, "created_at", None):
        prescription.created_at = datetime.now()

    oral_clean = []
    for med in (prescription.medications_oral or []):
        oral_clean.append({
            **med,
            "medication": strip_citations(med.get("medication", "")),
            "instructions": strip_citations(med.get("instructions", "")),
        })

    topical_clean = []
    for med in (prescription.medications_topical or []):
        topical_clean.append({
            **med,
            "medication": strip_citations(med.get("medication", "")),
            "instructions": strip_citations(med.get("instructions", "")),
        })

    template = _resolve_print_template(prescription)
    medications = oral_clean + topical_clean

    return render_template(
        template,
        prescription=prescription,
        patient=patient,
        doctor=prescription.doctor,
        oral_medications=oral_clean,
        topical_medications=topical_clean,
        medications=medications,
    )

@dermascribe_bp.route('/preview-print', methods=['POST'])
@login_required
def preview_print():
    """Renderiza a receita para impressão sem salvar no banco."""
    data = request.get_json() or {}

    patient_name = data.get('patient_name', 'Paciente')
    oral_medications = data.get('oral', [])
    topical_medications = data.get('topical', [])
    prescription_type = data.get('prescription_type', 'standard')

    VALID_TYPES = {'dermascribe', 'standard', 'antibiotico', 'isotretinoina'}
    if prescription_type not in VALID_TYPES:
        prescription_type = 'standard'

    class DummyPrescription:
        def __init__(self):
            self.id = 0
            self.created_at = datetime.now()
            self.prescription_type = prescription_type

    class DummyPatient:
        def __init__(self, name):
            self.name = name

    # Limpeza de citações
    for med in oral_medications:
        med["medication"] = strip_citations(med.get("medication", ""))
        med["instructions"] = strip_citations(med.get("instructions", ""))
    for med in topical_medications:
        med["medication"] = strip_citations(med.get("medication", ""))
        med["instructions"] = strip_citations(med.get("instructions", ""))

    template = PRINT_TEMPLATE_MAP.get(prescription_type, DEFAULT_PRINT_TEMPLATE)
    medications = oral_medications + topical_medications

    return render_template(
        template,
        prescription=DummyPrescription(),
        patient=DummyPatient(patient_name),
        doctor=current_user,
        oral_medications=oral_medications,
        topical_medications=topical_medications,
        medications=medications,
    )


@dermascribe_bp.route('/prescription/<int:prescription_id>/pdf')
@login_required
def prescription_pdf(prescription_id):
    prescription = (
        Prescription.query
        .options(joinedload(Prescription.doctor))
        .get_or_404(prescription_id)
    )

    patient = Patient.query.get_or_404(prescription.patient_id)

    if not getattr(prescription, "created_at", None):
        prescription.created_at = datetime.now()

    oral_clean = []
    for med in (prescription.medications_oral or []):
        oral_clean.append({
            **med,
            "medication": strip_citations(med.get("medication", "")),
            "instructions": strip_citations(med.get("instructions", "")),
        })

    topical_clean = []
    for med in (prescription.medications_topical or []):
        topical_clean.append({
            **med,
            "medication": strip_citations(med.get("medication", "")),
            "instructions": strip_citations(med.get("instructions", "")),
        })

    template = _resolve_print_template(prescription)
    medications = oral_clean + topical_clean

    html_str = render_template(
        template,
        prescription=prescription,
        patient=patient,
        doctor=prescription.doctor,
        oral_medications=oral_clean,
        topical_medications=topical_clean,
        medications=medications,
    )

    pdf = HTML(string=html_str, base_url=request.host_url).write_pdf()

    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'inline; filename=prescricao_{prescription_id}.pdf'
    return response
