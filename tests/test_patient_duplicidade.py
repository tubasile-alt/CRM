"""Testes de proteção contra duplicidade de pacientes.

Cobre: normalização de CPF/telefone no modelo, índice único parcial de CPF,
fim do attach silencioso por nome no agendamento, preenchimento sem
sobrescrita de dados de paciente existente e guarda de colisão na edição
do prontuário.
"""
import os
import unittest
from datetime import datetime

os.environ.setdefault('NEON_DATABASE_URL', 'sqlite:///:memory:')

from sqlalchemy.exc import IntegrityError

from app import app
from models import Appointment, Patient, User, db


class PatientDuplicidadeTestBase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app.config.update(TESTING=True, WTF_CSRF_ENABLED=False)
        cls.app = app

    def setUp(self):
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.drop_all()
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
            name='Secretária',
            role='secretaria',
            role_clinico='SECRETARY',
        )
        db.session.add_all([self.doctor, self.secretary])
        db.session.commit()

        self.client = self.app.test_client()

    def tearDown(self):
        db.session.rollback()
        db.drop_all()
        self.ctx.pop()

    def login(self, user):
        with self.client.session_transaction() as sess:
            sess['_user_id'] = str(user.id)
            sess['_fresh'] = True

    def add_patient(self, **kwargs):
        kwargs.setdefault('status_cadastral', 'ativo')
        patient = Patient(**kwargs)
        db.session.add(patient)
        db.session.commit()
        return patient

    def appointment_payload(self, **overrides):
        payload = {
            'patientName': 'Maria Souza',
            'start': '2026-08-10T10:00:00',
            'end': '2026-08-10T10:30:00',
            'doctor_id': self.doctor.id,
        }
        payload.update(overrides)
        return payload


class NormalizacaoModeloTests(PatientDuplicidadeTestBase):
    def test_validates_normaliza_cpf_mascarado(self):
        patient = self.add_patient(name='Ana Lima', cpf='123.456.789-00')
        self.assertEqual(patient.cpf, '12345678900')

    def test_validates_normaliza_telefone_e_vazio_vira_none(self):
        patient = self.add_patient(name='Ana Lima', phone='(11) 98888-7777', cpf='')
        self.assertEqual(patient.phone, '11988887777')
        self.assertIsNone(patient.cpf)

    def test_segundo_paciente_com_mesmo_cpf_dispara_integrity_error(self):
        self.add_patient(name='Ana Lima', cpf='12345678900')
        with self.assertRaises(IntegrityError):
            # Mesmo CPF com máscara diferente: normalização torna-o idêntico.
            self.add_patient(name='Outra Pessoa', cpf='123.456.789-00')
        db.session.rollback()

    def test_telefone_duplicado_e_permitido(self):
        self.add_patient(name='Mãe', phone='11988887777')
        filho = self.add_patient(name='Filho', phone='(11) 98888-7777')
        self.assertEqual(filho.phone, '11988887777')
        self.assertEqual(
            Patient.query.filter_by(phone='11988887777').count(), 2
        )


class CreateAppointmentTests(PatientDuplicidadeTestBase):
    def test_nome_exato_sem_patient_id_retorna_409_com_duplicates(self):
        existing = self.add_patient(name='Maria Souza')
        self.login(self.secretary)

        resp = self.client.post('/api/appointments', json=self.appointment_payload())

        self.assertEqual(resp.status_code, 409)
        data = resp.get_json()
        self.assertEqual(data['warning'], 'duplicate_found')
        self.assertTrue(data['duplicates'])
        first = data['duplicates'][0]
        self.assertEqual(first['id'], existing.id)
        self.assertTrue(first['exact'])
        # Nenhum agendamento foi anexado silenciosamente ao homônimo.
        self.assertEqual(len(existing.appointments), 0)

    def test_force_create_cria_novo_paciente_mesmo_com_homonimo(self):
        existing = self.add_patient(name='Maria Souza')
        self.login(self.secretary)

        resp = self.client.post(
            '/api/appointments',
            json=self.appointment_payload(force_create=True),
        )

        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.get_json()['success'])
        self.assertEqual(Patient.query.filter_by(name='Maria Souza').count(), 2)
        self.assertEqual(len(existing.appointments), 0)

    def test_patient_id_nao_sobrescreve_cpf_preenchido(self):
        existing = self.add_patient(
            name='Maria Souza', cpf='12345678900', phone='11911112222'
        )
        self.login(self.secretary)

        resp = self.client.post(
            '/api/appointments',
            json=self.appointment_payload(
                patient_id=existing.id,
                cpf='999.888.777-66',
                phone='11933334444',
                city='Campinas',
            ),
        )

        self.assertEqual(resp.status_code, 200)
        db.session.refresh(existing)
        self.assertEqual(existing.cpf, '12345678900')
        self.assertEqual(existing.phone, '11911112222')
        # Campo vazio é preenchido normalmente.
        self.assertEqual(existing.city, 'Campinas')

    def test_cpf_invalido_retorna_400(self):
        self.login(self.secretary)
        resp = self.client.post(
            '/api/appointments',
            json=self.appointment_payload(cpf='123', force_create=True),
        )
        self.assertEqual(resp.status_code, 400)


class UpdateAppointmentTests(PatientDuplicidadeTestBase):
    def test_renomear_paciente_ativo_pela_agenda_retorna_409(self):
        homonimo = self.add_patient(name='João Silva')
        patient = self.add_patient(name='João da Silva')
        appointment = Appointment(
            patient_id=patient.id,
            doctor_id=self.doctor.id,
            start_time=datetime(2026, 8, 10, 10, 0),
            end_time=datetime(2026, 8, 10, 10, 30),
        )
        db.session.add(appointment)
        db.session.commit()

        self.login(self.secretary)
        resp = self.client.put(
            f'/api/appointments/{appointment.id}',
            json={'patientName': 'João Silva'},
        )

        self.assertEqual(resp.status_code, 409)
        db.session.refresh(appointment)
        # Não re-vinculou ao homônimo nem renomeou o registro compartilhado.
        self.assertEqual(appointment.patient_id, patient.id)
        self.assertEqual(patient.name, 'João da Silva')
        self.assertEqual(homonimo.name, 'João Silva')


class UpdatePatientTests(PatientDuplicidadeTestBase):
    def test_mudar_nome_para_homonimo_sem_force_retorna_409(self):
        homonimo = self.add_patient(name='Carlos Pereira')
        patient = self.add_patient(name='Carlos Andrade')
        self.login(self.secretary)

        resp = self.client.post(
            f'/api/patient/{patient.id}/update',
            json={'name': 'Carlos Pereira'},
        )

        self.assertEqual(resp.status_code, 409)
        data = resp.get_json()
        self.assertEqual(data['warning'], 'duplicates_found')
        self.assertTrue(any(w['id'] == homonimo.id for w in data['warnings']))
        db.session.refresh(patient)
        self.assertEqual(patient.name, 'Carlos Andrade')

    def test_mudar_nome_para_homonimo_com_force_retorna_200(self):
        self.add_patient(name='Carlos Pereira')
        patient = self.add_patient(name='Carlos Andrade')
        self.login(self.secretary)

        resp = self.client.post(
            f'/api/patient/{patient.id}/update',
            json={'name': 'Carlos Pereira', 'force': True},
        )

        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.get_json()['success'])
        db.session.refresh(patient)
        self.assertEqual(patient.name, 'Carlos Pereira')

    def test_mudar_cpf_para_cpf_existente_retorna_409_mesmo_com_force(self):
        self.add_patient(name='Ana Lima', cpf='12345678900')
        patient = self.add_patient(name='Beatriz Costa', cpf='98765432100')
        self.login(self.secretary)

        # Sem force: guarda de colisão devolve os conflitos.
        resp = self.client.post(
            f'/api/patient/{patient.id}/update',
            json={'name': 'Beatriz Costa', 'cpf': '123.456.789-00'},
        )
        self.assertEqual(resp.status_code, 409)
        self.assertEqual(resp.get_json()['warning'], 'duplicates_found')

        # Com force: o índice único ainda impede o CPF duplicado (409).
        resp = self.client.post(
            f'/api/patient/{patient.id}/update',
            json={'name': 'Beatriz Costa', 'cpf': '123.456.789-00', 'force': True},
        )
        self.assertEqual(resp.status_code, 409)
        self.assertEqual(resp.get_json()['warning'], 'duplicate_found')
        db.session.rollback()
        db.session.refresh(patient)
        self.assertEqual(patient.cpf, '98765432100')

    def test_cpf_invalido_retorna_400(self):
        patient = self.add_patient(name='Ana Lima')
        self.login(self.secretary)
        resp = self.client.post(
            f'/api/patient/{patient.id}/update',
            json={'name': 'Ana Lima', 'cpf': '1234'},
        )
        self.assertEqual(resp.status_code, 400)


if __name__ == '__main__':
    unittest.main()
