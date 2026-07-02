import io
import json
import inspect
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch

from flask import Flask
from flask_login import LoginManager
from PIL import Image

from models import Appointment, Patient, PatientDoctor, PhysicalAgendaImportLog, User, db
from routes.physical_agenda import analyze, physical_agenda_bp
from services.physical_agenda_ai import _normalize_result, analyze_physical_agenda_image


ROOT = Path(__file__).resolve().parents[1]


def png_bytes():
    output = io.BytesIO()
    Image.new('RGB', (20, 20), 'white').save(output, 'PNG')
    return output.getvalue()


class PhysicalAgendaImportRouteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app = Flask(
            __name__,
            template_folder=str(ROOT / 'templates'),
            static_folder=str(ROOT / 'static'),
        )
        app.config.update(
            SECRET_KEY='test-secret',
            TESTING=True,
            WTF_CSRF_ENABLED=False,
            SQLALCHEMY_DATABASE_URI='sqlite:///:memory:',
            SQLALCHEMY_TRACK_MODIFICATIONS=False,
            OPENAI_API_KEY='test-key',
            OPENAI_VISION_MODEL='gpt-4.1-mini',
            PHYSICAL_AGENDA_UPLOAD_MAX_MB=10,
        )
        db.init_app(app)

        login_manager = LoginManager(app)

        @login_manager.user_loader
        def load_user(user_id):
            return db.session.get(User, int(user_id))

        app.register_blueprint(physical_agenda_bp)
        cls.app = app

        with app.app_context():
            User.__table__.create(bind=db.engine)
            Patient.__table__.create(bind=db.engine)
            PatientDoctor.__table__.create(bind=db.engine)
            Appointment.__table__.create(bind=db.engine)
            PhysicalAgendaImportLog.__table__.create(bind=db.engine)
            cls.doctor = User(
                username='doctor',
                email='doctor@example.com',
                password_hash='test',
                name='Dr. Teste',
                role='medico',
                role_clinico='DERM',
            )
            cls.other_doctor = User(
                username='doctor2',
                email='doctor2@example.com',
                password_hash='test',
                name='Dra. Outra',
                role='medico',
                role_clinico='DERM',
            )
            cls.secretary = User(
                username='secretary',
                email='secretary@example.com',
                password_hash='test',
                name='Secretária',
                role='secretaria',
                role_clinico='SECRETARY',
            )
            db.session.add_all([cls.doctor, cls.other_doctor, cls.secretary])
            active_patient = Patient(
                name='Maria Silva',
                phone='16999999999',
                cpf='123.456.789-01',
                status_cadastral='ativo',
            )
            provisional_patient = Patient(
                name='Ana Provisória',
                phone='16888888888',
                status_cadastral='provisorio',
            )
            db.session.add_all([active_patient, provisional_patient])
            db.session.flush()
            db.session.add_all([
                PatientDoctor(
                    patient_id=active_patient.id,
                    doctor_id=cls.doctor.id,
                    patient_code=1001,
                ),
                PatientDoctor(
                    patient_id=provisional_patient.id,
                    doctor_id=cls.doctor.id,
                    patient_code=None,
                ),
            ])
            db.session.commit()
            cls.doctor_id = cls.doctor.id
            cls.other_doctor_id = cls.other_doctor.id
            cls.secretary_id = cls.secretary.id
            cls.active_patient_id = active_patient.id
            cls.provisional_patient_id = provisional_patient.id

    @classmethod
    def tearDownClass(cls):
        with cls.app.app_context():
            db.session.remove()
            db.drop_all()

    def setUp(self):
        self.client = self.app.test_client()
        self.login(self.secretary_id)
        self.app.config['OPENAI_API_KEY'] = 'test-key'
        with self.app.app_context():
            db.session.execute(PhysicalAgendaImportLog.__table__.delete())
            db.session.execute(Appointment.__table__.delete())
            db.session.commit()

    def login(self, user_id):
        with self.client.session_transaction() as session:
            session['_user_id'] = str(user_id)
            session['_fresh'] = True

    def base_form(self):
        return {'date': '2026-07-01', 'doctor_id': str(self.doctor_id)}

    def import_item(self, **overrides):
        item = {
            'agenda_date': '2026-07-02',
            'time': '09:00',
            'duration_minutes': 5,
            'patient_id': self.active_patient_id,
            'appointment_type': 'retorno',
            'procedure': '',
            'notes': '',
            'idempotency_key': 'test-import-key-000000000001',
        }
        item.update(overrides)
        return item

    @patch('routes.physical_agenda.render_template', return_value='physical agenda page')
    def test_get_page_loads_template(self, render_template_mock):
        response = self.client.get('/agenda/importar-fisica')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_data(as_text=True), 'physical agenda page')
        self.assertEqual(render_template_mock.call_args.args[0], 'physical_agenda_import.html')

    def test_analyze_rejects_missing_file(self):
        response = self.client.post('/api/agenda-fisica/analisar', data=self.base_form())
        self.assertEqual(response.status_code, 400)
        self.assertIn('Selecione uma imagem', response.get_json()['error'])

    def test_analyze_rejects_invalid_extension(self):
        data = self.base_form()
        data['image'] = (io.BytesIO(b'not-an-image'), 'agenda.txt')
        response = self.client.post('/api/agenda-fisica/analisar', data=data)
        self.assertEqual(response.status_code, 400)
        self.assertIn('Formato inválido', response.get_json()['error'])

    def test_analyze_reports_missing_openai_key(self):
        self.app.config['OPENAI_API_KEY'] = None
        data = self.base_form()
        data['image'] = (io.BytesIO(png_bytes()), 'agenda.png')
        response = self.client.post('/api/agenda-fisica/analisar', data=data)
        self.assertEqual(response.status_code, 503)
        self.assertIn('OPENAI_API_KEY não configurada', response.get_json()['error'])

    def test_doctor_cannot_analyze_another_doctors_agenda(self):
        self.login(self.doctor_id)
        data = {
            'date': '2026-07-01',
            'doctor_id': str(self.other_doctor_id),
            'image': (io.BytesIO(png_bytes()), 'agenda.png'),
        }
        response = self.client.post('/api/agenda-fisica/analisar', data=data)
        self.assertEqual(response.status_code, 403)

    @patch('routes.physical_agenda.analyze_physical_agenda_image')
    def test_success_returns_review_data_without_database_writes(self, analyze_mock):
        analyze_mock.return_value = {
            'items': [{
                'time': '09:00',
                'patient_name': 'Paciente Teste',
                'phone': '16999999999',
                'appointment_type': 'retorno',
                'procedure': None,
                'notes': None,
                'confidence': 0.92,
                'raw_text': '09 Paciente Teste ret',
            }],
            'warnings': [],
        }
        data = self.base_form()
        data['image'] = (io.BytesIO(png_bytes()), 'agenda.png')

        with self.app.app_context():
            patients_before = Patient.query.count()
        response = self.client.post('/api/agenda-fisica/analisar', data=data)
        with self.app.app_context():
            patients_after = Patient.query.count()
            self.assertFalse(db.session.new)
            self.assertFalse(db.session.dirty)
            self.assertFalse(db.session.deleted)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.get_json()['success'])
        self.assertEqual(patients_before, patients_after)

    def test_analysis_route_has_no_database_write_calls(self):
        source = inspect.getsource(analyze)
        self.assertNotIn('db.session', source)
        self.assertNotIn('Patient(', source)
        self.assertNotIn('Appointment(', source)

    def test_suggestions_only_return_active_patients(self):
        response = self.client.post('/api/agenda-fisica/sugerir-pacientes', json={
            'doctor_id': self.doctor_id,
            'items': [
                {'patient_name': 'Maria Silva', 'phone': '16999999999'},
                {'patient_name': 'Ana Provisória', 'phone': '16888888888'},
            ],
        })
        self.assertEqual(response.status_code, 200)
        matches = response.get_json()['matches']
        self.assertEqual(matches[0]['suggestions'][0]['patient_id'], self.active_patient_id)
        self.assertEqual(matches[1]['suggestions'], [])

    def test_suggestions_match_exact_cpf_or_patient_code(self):
        response = self.client.post('/api/agenda-fisica/sugerir-pacientes', json={
            'doctor_id': self.doctor_id,
            'items': [
                {'patient_name': '', 'phone': '', 'cpf': '12345678901'},
                {'patient_name': '', 'phone': '', 'patient_code': '1001'},
            ],
        })
        self.assertEqual(response.status_code, 200)
        matches = response.get_json()['matches']
        self.assertEqual(matches[0]['suggestions'][0]['patient_id'], self.active_patient_id)
        self.assertEqual(matches[1]['suggestions'][0]['patient_id'], self.active_patient_id)
        self.assertIn('CPF exato', matches[0]['suggestions'][0]['reason'])
        self.assertIn('código exato', matches[1]['suggestions'][0]['reason'])

    def test_active_duplicate_blocks_provisional_creation(self):
        with self.app.app_context():
            patients_before = Patient.query.count()
        response = self.client.post('/api/agenda-fisica/pacientes-provisorios', json={
            'doctor_id': self.doctor_id,
            'patient_name': 'Maria Silva',
            'phone': '16999999999',
        })
        with self.app.app_context():
            patients_after = Patient.query.count()
        self.assertEqual(response.status_code, 409)
        self.assertTrue(response.get_json()['suggestions'])
        self.assertEqual(patients_before, patients_after)

    def test_existing_provisional_is_reused_instead_of_duplicated(self):
        response = self.client.post('/api/agenda-fisica/pacientes-provisorios', json={
            'doctor_id': self.doctor_id,
            'patient_name': 'Ana Provisória',
            'phone': '16888888888',
        })
        self.assertEqual(response.status_code, 409)
        existing = response.get_json()['existing_provisional']
        self.assertEqual(existing['patient_id'], self.provisional_patient_id)

    def test_explicit_action_creates_provisional_without_patient_code(self):
        response = self.client.post('/api/agenda-fisica/pacientes-provisorios', json={
            'doctor_id': self.doctor_id,
            'patient_name': 'Nova Pessoa',
            'phone': '16777777777',
        })
        self.assertEqual(response.status_code, 201)
        patient_id = response.get_json()['patient']['patient_id']
        with self.app.app_context():
            patient = db.session.get(Patient, patient_id)
            link = PatientDoctor.query.filter_by(patient_id=patient_id, doctor_id=self.doctor_id).one()
            self.assertEqual(patient.status_cadastral, 'provisorio')
            self.assertIsNone(link.patient_code)
            db.session.execute(
                PatientDoctor.__table__.delete().where(PatientDoctor.patient_id == patient_id)
            )
            db.session.execute(Patient.__table__.delete().where(Patient.id == patient_id))
            db.session.commit()

    def test_drag_and_drop_is_available(self):
        template = (ROOT / 'templates' / 'physical_agenda_import.html').read_text(encoding='utf-8')
        script = (ROOT / 'static' / 'js' / 'physical-agenda-import.js').read_text(encoding='utf-8')
        self.assertIn('id="agenda-drop-zone"', template)
        self.assertIn("dropZone.addEventListener('drop'", script)

    def test_multiple_images_have_individual_dates(self):
        template = (ROOT / 'templates' / 'physical_agenda_import.html').read_text(encoding='utf-8')
        script = (ROOT / 'static' / 'js' / 'physical-agenda-import.js').read_text(encoding='utf-8')
        self.assertIn('id="agenda-image-list"', template)
        self.assertIn('accept="image/jpeg,image/png,image/webp" multiple', template)
        self.assertIn("date.className = 'form-control form-control-sm agenda-image-date'", script)
        self.assertIn('for (let index = 0; index < imageQueue.length; index += 1)', script)
        self.assertIn('agenda_date: analysis.agenda_date', script)
        self.assertIn('id="confirm-import-button"', template)
        self.assertIn('Importar para agenda', template)
        self.assertNotIn('copy-json-button', template)
        self.assertNotIn('download-json-button', template)
        self.assertNotIn('copyJson', script)
        self.assertNotIn('downloadJson', script)
        self.assertIn("fetch('/api/agenda-fisica/importar'", script)
        self.assertIn('duration_minutes: 5', script)

    def test_import_preview_allows_automatic_patient_resolution(self):
        response = self.client.post('/api/agenda-fisica/previsualizar-importacao', json={
            'doctor_id': self.doctor_id,
            'items': [self.import_item(patient_id=None)],
        })
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertTrue(payload['ready'])

    def test_import_preview_detects_existing_appointment_conflict(self):
        with self.app.app_context():
            start = datetime(2026, 7, 2, 9, 0)
            db.session.add(Appointment(
                patient_id=self.active_patient_id,
                doctor_id=self.doctor_id,
                start_time=start,
                end_time=start + timedelta(minutes=15),
                status='agendado',
            ))
            db.session.commit()

        response = self.client.post('/api/agenda-fisica/previsualizar-importacao', json={
            'doctor_id': self.doctor_id,
            'items': [self.import_item()],
        })
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertTrue(payload['ready'])
        self.assertTrue(payload['rows'][0]['time_adjusted'])
        self.assertEqual(payload['rows'][0]['start'], '2026-07-02T09:15')

    def test_import_preview_ignores_cancelled_appointment(self):
        with self.app.app_context():
            start = datetime(2026, 7, 2, 9, 5)
            db.session.add(Appointment(
                patient_id=self.active_patient_id,
                doctor_id=self.doctor_id,
                start_time=start,
                end_time=start + timedelta(minutes=15),
                status='cancelado',
            ))
            db.session.commit()

        response = self.client.post('/api/agenda-fisica/previsualizar-importacao', json={
            'doctor_id': self.doctor_id,
            'items': [self.import_item()],
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.get_json()['ready'])

    def test_import_preview_fits_overlaps_inside_batch(self):
        response = self.client.post('/api/agenda-fisica/previsualizar-importacao', json={
            'doctor_id': self.doctor_id,
            'items': [
                self.import_item(duration_minutes=30),
                self.import_item(
                    time='09:15',
                    idempotency_key='test-import-key-000000000002',
                ),
            ],
        })
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertTrue(payload['ready'])
        self.assertEqual(payload['rows'][1]['start'], '2026-07-02T09:30')
        self.assertTrue(payload['rows'][1]['time_adjusted'])

    def test_conflicting_batch_is_fitted_into_free_slots(self):
        response = self.client.post('/api/agenda-fisica/importar', json={
            'doctor_id': self.doctor_id,
            'confirmed': True,
            'items': [
                self.import_item(duration_minutes=30),
                self.import_item(
                    time='09:15',
                    idempotency_key='test-import-key-000000000003',
                ),
            ],
        })
        self.assertEqual(response.status_code, 201)
        payload = response.get_json()
        self.assertEqual(payload['appointments'][0]['start'], '2026-07-02T09:00')
        self.assertEqual(payload['appointments'][1]['start'], '2026-07-02T09:30')
        with self.app.app_context():
            self.assertEqual(Appointment.query.count(), 2)
            self.assertEqual(PhysicalAgendaImportLog.query.count(), 2)

    def test_import_requires_explicit_confirmation(self):
        response = self.client.post('/api/agenda-fisica/importar', json={
            'doctor_id': self.doctor_id,
            'items': [self.import_item()],
        })
        self.assertEqual(response.status_code, 400)
        with self.app.app_context():
            self.assertEqual(Appointment.query.count(), 0)

    def test_doctor_cannot_import_for_another_doctor(self):
        self.login(self.doctor_id)
        response = self.client.post('/api/agenda-fisica/previsualizar-importacao', json={
            'doctor_id': self.other_doctor_id,
            'items': [self.import_item()],
        })
        self.assertEqual(response.status_code, 403)

    def test_confirmed_import_creates_appointment_and_audit_log(self):
        response = self.client.post('/api/agenda-fisica/importar', json={
            'doctor_id': self.doctor_id,
            'confirmed': True,
            'items': [self.import_item(procedure='Botox', notes='Retorno')],
        })
        self.assertEqual(response.status_code, 201)
        payload = response.get_json()
        self.assertEqual(payload['created_count'], 1)
        with self.app.app_context():
            appointment = db.session.get(Appointment, payload['appointments'][0]['appointment_id'])
            self.assertEqual(appointment.patient_id, self.active_patient_id)
            self.assertEqual(appointment.status, 'agendado')
            self.assertIn('Procedimento: Botox', appointment.notes)
            audit = PhysicalAgendaImportLog.query.filter_by(appointment_id=appointment.id).one()
            self.assertEqual(audit.performed_by_user_id, self.secretary_id)

    def test_reimport_is_blocked_without_duplicate_appointment(self):
        request_data = {
            'doctor_id': self.doctor_id,
            'confirmed': True,
            'items': [self.import_item()],
        }
        first = self.client.post('/api/agenda-fisica/importar', json=request_data)
        second = self.client.post('/api/agenda-fisica/importar', json=request_data)
        self.assertEqual(first.status_code, 201)
        self.assertEqual(second.status_code, 400)
        with self.app.app_context():
            self.assertEqual(Appointment.query.count(), 1)
            self.assertEqual(PhysicalAgendaImportLog.query.count(), 1)

    def test_duplicate_irregular_times_use_five_minute_slots(self):
        response = self.client.post('/api/agenda-fisica/importar', json={
            'doctor_id': self.doctor_id,
            'confirmed': True,
            'items': [
                self.import_item(time='09:01', duration_minutes=None),
                self.import_item(
                    time='09:01',
                    duration_minutes=None,
                    idempotency_key='test-import-key-000000000004',
                ),
            ],
        })
        self.assertEqual(response.status_code, 201)
        appointments = response.get_json()['appointments']
        self.assertEqual([item['start'] for item in appointments], [
            '2026-07-02T09:00',
            '2026-07-02T09:05',
        ])
        self.assertTrue(all(item['time_adjusted'] for item in appointments))

    def test_short_phone_value_can_resolve_patient_code(self):
        response = self.client.post('/api/agenda-fisica/importar', json={
            'doctor_id': self.doctor_id,
            'confirmed': True,
            'items': [self.import_item(
                patient_id=None,
                patient_name='Maria',
                phone='1001',
            )],
        })
        self.assertEqual(response.status_code, 201)
        appointment = response.get_json()['appointments'][0]
        self.assertEqual(appointment['patient_id'], self.active_patient_id)
        self.assertEqual(appointment['patient_resolution'], 'ativo_encontrado')

class PhysicalAgendaAIValidationTests(unittest.TestCase):
    def test_result_is_normalized_after_model_response(self):
        result = _normalize_result({
            'items': [{
                'time': '25:90',
                'patient_name': '  Paciente   Teste  ',
                'phone': '(16) 99999-9999',
                'appointment_type': ' retorno ',
                'procedure': None,
                'notes': '',
                'confidence': 3,
                'raw_text': ' linha original ',
                'unexpected': 'discarded',
            }],
            'warnings': ['  conferir telefone  '],
        })

        item = result['items'][0]
        self.assertIsNone(item['time'])
        self.assertEqual(item['patient_name'], 'Paciente Teste')
        self.assertEqual(item['phone'], '16999999999')
        self.assertEqual(item['confidence'], 1.0)
        self.assertNotIn('unexpected', item)
        self.assertEqual(result['warnings'], ['conferir telefone'])

    @patch('openai.OpenAI')
    def test_service_uses_multimodal_responses_without_storage(self, openai_mock):
        response_payload = {
            'items': [{
                'time': '09:00',
                'patient_name': 'Paciente',
                'phone': None,
                'appointment_type': 'retorno',
                'procedure': None,
                'notes': None,
                'confidence': 0.9,
                'raw_text': '09 Paciente ret',
            }],
            'warnings': [],
        }
        client = openai_mock.return_value
        client.responses.create.return_value.output_text = json.dumps(response_payload)
        app = Flask(__name__)
        app.config.update(OPENAI_API_KEY='test-key', OPENAI_VISION_MODEL='gpt-4.1-mini')

        with app.app_context():
            result = analyze_physical_agenda_image(
                image_bytes=png_bytes(),
                mime_type='image/png',
                agenda_date='2026-07-01',
                doctor_name='Dr. Teste',
            )

        self.assertEqual(result['items'][0]['time'], '09:00')
        request = client.responses.create.call_args.kwargs
        self.assertEqual(request['model'], 'gpt-4.1-mini')
        self.assertFalse(request['store'])
        self.assertEqual(request['text']['format']['type'], 'json_schema')
        image_content = request['input'][0]['content'][1]
        self.assertEqual(image_content['type'], 'input_image')
        self.assertTrue(image_content['image_url'].startswith('data:image/png;base64,'))


if __name__ == '__main__':
    unittest.main()
