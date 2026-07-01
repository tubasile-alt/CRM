import io
import json
import unittest
from pathlib import Path
from unittest.mock import patch

from flask import Flask
from flask_login import LoginManager
from PIL import Image

from models import User, db
from routes.physical_agenda import physical_agenda_bp
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
            db.session.commit()
            cls.doctor_id = cls.doctor.id
            cls.other_doctor_id = cls.other_doctor.id
            cls.secretary_id = cls.secretary.id

    @classmethod
    def tearDownClass(cls):
        with cls.app.app_context():
            db.session.remove()
            db.drop_all()

    def setUp(self):
        self.client = self.app.test_client()
        self.login(self.secretary_id)
        self.app.config['OPENAI_API_KEY'] = 'test-key'

    def login(self, user_id):
        with self.client.session_transaction() as session:
            session['_user_id'] = str(user_id)
            session['_fresh'] = True

    def base_form(self):
        return {'date': '2026-07-01', 'doctor_id': str(self.doctor_id)}

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
            users_before = User.query.count()
        response = self.client.post('/api/agenda-fisica/analisar', data=data)
        with self.app.app_context():
            users_after = User.query.count()
            self.assertFalse(db.session.new)
            self.assertFalse(db.session.dirty)
            self.assertFalse(db.session.deleted)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.get_json()['success'])
        self.assertEqual(users_before, users_after)

    def test_route_source_has_no_database_write_calls(self):
        source = (ROOT / 'routes' / 'physical_agenda.py').read_text(encoding='utf-8')
        self.assertNotIn('db.session', source)
        self.assertNotIn('Patient(', source)
        self.assertNotIn('Appointment(', source)

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
