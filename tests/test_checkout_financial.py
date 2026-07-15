import unittest
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch

from flask import Flask
from flask_login import LoginManager

from models import Appointment, CosmeticProcedurePlan, Note, Patient, Payment, User, db
from routes.checkout_api import checkout_api_bp
from routes.cosmetic_api import cosmetic_api_bp
from services.clinic_time import get_brazil_time


ROOT = Path(__file__).resolve().parents[1]


class FinancialCheckoutTests(unittest.TestCase):
    def setUp(self):
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
        )
        db.init_app(app)

        login_manager = LoginManager(app)

        @login_manager.user_loader
        def load_user(user_id):
            return db.session.get(User, int(user_id))

        app.register_blueprint(checkout_api_bp)
        app.register_blueprint(cosmetic_api_bp)
        self.app = app
        self.client = app.test_client()

        with app.app_context():
            db.create_all()
            self.doctor = User(
                username='doctor',
                email='doctor@example.com',
                password_hash='test',
                name='Dr. Teste',
                role='medico',
                role_clinico='DERM',
            )
            self.secretary = User(
                username='secretary',
                email='secretary@example.com',
                password_hash='test',
                name='Secretaria',
                role='secretaria',
                role_clinico='SECRETARY',
            )
            self.patient = Patient(name='Maria Checkout', phone='16999999999')
            db.session.add_all([self.doctor, self.secretary, self.patient])
            db.session.flush()

            self.appointment = Appointment(
                patient_id=self.patient.id,
                doctor_id=self.doctor.id,
                start_time=datetime(2026, 7, 15, 10, 0),
                end_time=datetime(2026, 7, 15, 10, 30),
                appointment_type='Particular',
                status='agendado',
            )
            db.session.add(self.appointment)
            db.session.flush()

            self.note = Note(
                patient_id=self.patient.id,
                doctor_id=self.doctor.id,
                appointment_id=self.appointment.id,
                note_type='conduta',
                category='cosmiatria',
                content='Plano',
            )
            db.session.add(self.note)
            db.session.flush()

            self.plan = CosmeticProcedurePlan(
                note_id=self.note.id,
                name='Botox',
                procedure_name='Botox',
                planned_value=900,
                final_budget=850,
                follow_up_months=5,
            )
            db.session.add(self.plan)
            db.session.commit()

            self.doctor_id = self.doctor.id
            self.secretary_id = self.secretary.id
            self.patient_id = self.patient.id
            self.appointment_id = self.appointment.id
            self.plan_id = self.plan.id

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def login(self, user_id):
        with self.client.session_transaction() as session:
            session['_user_id'] = str(user_id)
            session['_fresh'] = True

    @patch('threading.Thread')
    def test_realized_cosmetic_execution_creates_pending_checkout(self, thread_mock):
        self.login(self.doctor_id)

        response = self.client.post(
            f'/api/cosmetic-plans/{self.plan_id}/executions',
            json={
                'execution_status': 'realizada',
                'performed_date': '2026-07-15',
                'charged_value': 850,
            },
        )

        self.assertEqual(response.status_code, 201)
        body = response.get_json()
        self.assertTrue(body['success'])
        self.assertIsNotNone(body['payment_id'])
        thread_mock.assert_called_once()

        with self.app.app_context():
            payment = Payment.query.one()
            self.assertEqual(payment.status, 'pendente')
            self.assertEqual(payment.patient_id, self.patient_id)
            self.assertEqual(payment.appointment_id, self.appointment_id)
            self.assertEqual(float(payment.total_amount), 1250.0)
            names = [item['name'] for item in payment.procedures]
            self.assertEqual(names, ['Consulta Particular', 'Botox'])

    def test_checkout_list_separates_today_and_old_pending(self):
        today = get_brazil_time()
        old_day = today - timedelta(days=3)

        with self.app.app_context():
            db.session.add_all([
                Payment(
                    patient_id=self.patient_id,
                    appointment_id=self.appointment_id,
                    total_amount=100,
                    payment_method='pendente',
                    status='pendente',
                    procedures=[{'name': 'Hoje', 'value': 100}],
                    consultation_type='Particular',
                    created_at=today,
                ),
                Payment(
                    patient_id=self.patient_id,
                    appointment_id=self.appointment_id,
                    total_amount=200,
                    payment_method='pendente',
                    status='pendente',
                    procedures=[{'name': 'Antigo', 'value': 200}],
                    consultation_type='Particular',
                    created_at=old_day,
                ),
                Payment(
                    patient_id=self.patient_id,
                    appointment_id=self.appointment_id,
                    total_amount=300,
                    payment_method='pix',
                    status='pago',
                    procedures=[{'name': 'Pago', 'value': 300}],
                    consultation_type='Particular',
                    created_at=today,
                    paid_at=today,
                ),
            ])
            db.session.commit()

        self.login(self.secretary_id)
        response = self.client.get('/api/checkout/pending')

        self.assertEqual(response.status_code, 200)
        groups = response.get_json()['groups']
        self.assertEqual(len(groups['today_pending']), 1)
        self.assertEqual(len(groups['old_pending']), 1)
        self.assertEqual(len(groups['today_paid']), 1)
        self.assertEqual(groups['old_pending'][0]['procedures'][0]['name'], 'Antigo')

    def test_pending_count_includes_old_pending(self):
        today = get_brazil_time()
        old_day = today - timedelta(days=2)

        with self.app.app_context():
            db.session.add_all([
                Payment(
                    patient_id=self.patient_id,
                    total_amount=100,
                    payment_method='pendente',
                    status='pendente',
                    procedures=[{'name': 'Hoje', 'value': 100}],
                    consultation_type='Particular',
                    created_at=today,
                ),
                Payment(
                    patient_id=self.patient_id,
                    total_amount=200,
                    payment_method='pendente',
                    status='pendente',
                    procedures=[{'name': 'Antigo', 'value': 200}],
                    consultation_type='Particular',
                    created_at=old_day,
                ),
            ])
            db.session.commit()

        self.login(self.secretary_id)
        response = self.client.get('/api/checkout/pending/count')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()['count'], 2)


if __name__ == '__main__':
    unittest.main()
