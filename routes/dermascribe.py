from flask import Blueprint, render_template, request, jsonify, send_file
from flask_login import login_required, current_user
from models import db, Medication, MedicationUsage, Prescription, Patient
from services.openai_service import suggest_medications
import io
import csv
from datetime import datetime

dermascribe_bp = Blueprint('dermascribe', __name__, url_prefix='/dermascribe')

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
    
    if not medication_name:
        return jsonify({'status': 'error', 'message': 'Nome do medicamento é obrigatório'})
    
    existing = Medication.query.filter(
        Medication.name.ilike(medication_name)
    ).first()
    
    if existing:
        return jsonify({'status': 'exists', 'message': 'Medicamento já existe no banco'})
    
    new_medication = Medication(
        name=medication_name,
        type=medication_type,
        instructions=instructions
    )
    
    db.session.add(new_medication)
    db.session.commit()
    
    return jsonify({'status': 'success', 'message': 'Medicamento salvo com sucesso', 'id': new_medication.id})

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
    
    patient = Patient.query.get(patient_id)
    if not patient:
        return jsonify({'status': 'error', 'message': 'Paciente não encontrado'})
    
    prescription = Prescription(
        patient_id=patient_id,
        doctor_id=current_user.id,
        medications_oral=oral_medications,
        medications_topical=topical_medications,
        prescription_type='dermascribe'
    )
    
    db.session.add(prescription)
    
    all_medications = oral_medications + topical_medications
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
    
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': 'Receita salva com sucesso',
        'prescription_id': prescription.id
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
