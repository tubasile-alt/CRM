import json
import unittest
from datetime import date, datetime
from pathlib import Path
from unittest.mock import patch

from flask import Flask

from models import (
    Appointment,
    CosmeticProcedurePlan,
    Evolution,
    Note,
    Patient,
    PatientDoctor,
    Prescription,
    TransplantSurgeryRecord,
    User,
    db,
)
from services.prontuario_summary_ai import (
    ProntuarioSummaryAIError,
    build_prontuario_summary_source,
    generate_prontuario_summary,
)


ROOT = Path(__file__).resolve().parents[1]


def read_source(path):
    return (ROOT / path).read_text(encoding='utf-8')


class ProntuarioAISummaryServiceTests(unittest.TestCase):
    def setUp(self):
        app = Flask(__name__)
        app.config.update(
            SECRET_KEY='test-secret',
            TESTING=True,
            SQLALCHEMY_DATABASE_URI='sqlite:///:memory:',
            SQLALCHEMY_TRACK_MODIFICATIONS=False,
            OPENAI_API_KEY='test-key',
            OPENAI_SUMMARY_MODEL='gpt-summary-test',
        )
        db.init_app(app)
        self.app = app

        with app.app_context():
            db.create_all()
            doctor = User(
                username='doctor-summary',
                email='doctor-summary@example.com',
                password_hash='test',
                name='Dr. Resumo',
                role='medico',
                role_clinico='DERM',
            )
            patient = Patient(
                name='Maria Identificada',
                phone='16999999999',
                email='maria@example.com',
                cpf='123.456.789-01',
                address='Rua Sensível 123',
                birth_date=date(1990, 1, 1),
                allergies='Alergia a dipirona',
                attention_note='Medo de agulha',
            )
            db.session.add_all([doctor, patient])
            db.session.flush()
            appointment = Appointment(
                patient_id=patient.id,
                doctor_id=doctor.id,
                start_time=datetime(2026, 8, 20, 10, 0),
                end_time=datetime(2026, 8, 20, 10, 30),
                appointment_type='Cosmiatria',
                status='atendido',
            )
            db.session.add(appointment)
            db.session.flush()
            note = Note(
                patient_id=patient.id,
                doctor_id=doctor.id,
                appointment_id=appointment.id,
                note_type='queixa',
                category='cosmiatria',
                content=(
                    'Maria Identificada relatou acne. CPF 123.456.789-01, '
                    'telefone 16999999999 e email maria@example.com.'
                ),
            )
            db.session.add(note)
            db.session.flush()
            db.session.add_all([
                PatientDoctor(patient_id=patient.id, doctor_id=doctor.id, patient_code=1001),
                Evolution(
                    patient_id=patient.id,
                    doctor_id=doctor.id,
                    consultation_id=appointment.id,
                    evolution_date=datetime(2026, 8, 21, 9, 0),
                    content='Melhora parcial das lesões.',
                ),
                CosmeticProcedurePlan(
                    note_id=note.id,
                    name='Botox',
                    procedure_name='Botox',
                    status='ativo',
                ),
                Prescription(
                    patient_id=patient.id,
                    doctor_id=doctor.id,
                    appointment_id=appointment.id,
                    medications_oral=[{'medication': 'Isotretinoína 20mg'}],
                    medications_topical=['Adapaleno gel'],
                    summary='Tratamento acne',
                ),
                TransplantSurgeryRecord(
                    patient_id=patient.id,
                    doctor_id=doctor.id,
                    surgery_date=date(2026, 8, 22),
                    surgery_type='Teste',
                    observations='Sem intercorrências',
                ),
            ])
            db.session.commit()
            self.patient_id = patient.id

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_source_payload_excludes_and_redacts_identifiers(self):
        with self.app.app_context():
            payload, source_hash, has_content = build_prontuario_summary_source(self.patient_id)

        serialized = json.dumps(payload, ensure_ascii=False)
        self.assertTrue(has_content)
        self.assertEqual(len(source_hash), 64)
        self.assertIn('[paciente]', serialized)
        self.assertIn('[cpf]', serialized)
        self.assertIn('[telefone]', serialized)
        self.assertIn('[email]', serialized)
        self.assertNotIn('Maria Identificada', serialized)
        self.assertNotIn('16999999999', serialized)
        self.assertNotIn('123.456.789-01', serialized)
        self.assertNotIn('maria@example.com', serialized)
        self.assertNotIn('Rua Sensível', serialized)
        self.assertIn('Adapaleno gel', serialized)

    def test_missing_openai_key_is_friendly(self):
        with self.app.app_context():
            self.app.config['OPENAI_API_KEY'] = None
            with self.assertRaises(ProntuarioSummaryAIError) as ctx:
                generate_prontuario_summary({'schema': 'prontuario_resumo_v1'})
        self.assertIn('OPENAI_API_KEY não configurada', str(ctx.exception))

    @patch('openai.OpenAI')
    def test_generate_uses_responses_json_schema_without_storage(self, openai_mock):
        client = openai_mock.return_value
        client.responses.create.return_value.output_text = json.dumps({
            'summary': 'Quadro estável com conduta recente.',
            'alerts': ['Alergia a dipirona'],
            'pending': ['Reavaliar em 30 dias'],
        })

        with self.app.app_context():
            result, model = generate_prontuario_summary({
                'schema': 'prontuario_resumo_v1',
                'consultas': [{'data': '2026-08-20', 'notas': {'q': 'acne'}}],
            })

        request = client.responses.create.call_args.kwargs
        self.assertEqual(model, 'gpt-summary-test')
        self.assertFalse(request['store'])
        self.assertLessEqual(request['max_output_tokens'], 700)
        self.assertTrue(request['text']['format']['strict'])
        self.assertEqual(request['text']['format']['name'], 'prontuario_ai_summary')
        self.assertEqual(result['summary'], 'Quadro estável com conduta recente.')


def test_prontuario_ai_summary_ui_contract():
    template = read_source('templates/prontuario.html')
    js_source = read_source('static/js/prontuario.js')

    assert 'id="prontuarioAISummaryCard"' in template
    assert 'Resumo IA' in template
    assert 'id="aiSummaryRefreshBtn"' in template
    assert '/api/patient/${patientId}/ai-summary`' in js_source
    assert '/api/patient/${patientId}/ai-summary/generate`' in js_source
    assert 'window.refreshAISummary = refreshAISummary;' in js_source


def test_patient_ai_summary_model_is_separate_from_notes():
    source = read_source('models.py')

    assert 'class PatientAISummary(db.Model):' in source
    assert "__tablename__ = 'patient_ai_summary'" in source
    assert 'summary_text = db.Column(db.Text, nullable=False)' in source
