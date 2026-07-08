"""Testes da auditoria de duplicidades (/api/admin/audit-patients).

Cobre: normalização de acentos e dígitos, agrupamento de telefone/CPF
formatados vs só dígitos, homônimos com médicos distintos (risco médio),
score composto (birth_date/CPF como sinais a favor e contra) e clusters
de registros conectados via union-find em related_ids.

A auditoria é somente leitura: os testes apenas consultam o endpoint.
"""
import os
import unittest
from datetime import date

os.environ.setdefault('NEON_DATABASE_URL', 'sqlite:///:memory:')

from app import app, normalize_digits, normalize_patient_name
from models import Patient, PatientDoctor, User, db

# Categorias de alerta que indicam suspeita de duplicidade (excluí
# sem_código/mesmo_código/revisar_manualmente, que não são pareamento).
DUP_CATEGORIES = {'provável_duplicado', 'possível_duplicado', 'mesmo_cpf', 'mesmo_telefone'}


class AuditDuplicatesTestBase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app.config.update(TESTING=True, WTF_CSRF_ENABLED=False)
        cls.app = app

    def setUp(self):
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.drop_all()
        db.create_all()

        self.doctor1 = User(
            username='doc1', email='doc1@example.com', password_hash='test',
            name='Dr. Um', role='medico', role_clinico='DERM',
        )
        self.doctor2 = User(
            username='doc2', email='doc2@example.com', password_hash='test',
            name='Dr. Dois', role='medico', role_clinico='CP',
        )
        self.secretary = User(
            username='secretary', email='secretary@example.com', password_hash='test',
            name='Secretária', role='secretaria', role_clinico='SECRETARY',
        )
        db.session.add_all([self.doctor1, self.doctor2, self.secretary])
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

    def link(self, patient, doctor, code):
        pd = PatientDoctor(patient_id=patient.id, doctor_id=doctor.id, patient_code=code)
        db.session.add(pd)
        db.session.commit()
        return pd

    def set_raw_phone(self, patient_id, value):
        """Grava telefone via SQL cru, contornando a normalização do modelo
        (simula dado legado formatado ainda presente no banco)."""
        db.session.execute(
            db.text('UPDATE patient SET phone = :v WHERE id = :id'),
            {'v': value, 'id': patient_id},
        )
        db.session.commit()

    def set_raw_cpf(self, patient_id, value):
        """Grava CPF via SQL cru, contornando a normalização do modelo."""
        db.session.execute(
            db.text('UPDATE patient SET cpf = :v WHERE id = :id'),
            {'v': value, 'id': patient_id},
        )
        db.session.commit()

    def fetch_records(self):
        self.login(self.secretary)
        resp = self.client.get('/api/admin/audit-patients')
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data['success'])
        return data['records']

    def dup_records_for(self, records, patient_id, category=None):
        cats = {category} if category else DUP_CATEGORIES
        return [r for r in records if r['id'] == patient_id and r['category'] in cats]


class NormalizacaoHelpersTests(unittest.TestCase):
    def test_normalize_patient_name_remove_acentos(self):
        self.assertEqual(
            normalize_patient_name('João Silva'),
            normalize_patient_name('Joao Silva'),
        )
        self.assertEqual(normalize_patient_name('  José   ÁVILA '), 'jose avila')

    def test_normalize_digits_extrai_apenas_digitos(self):
        self.assertEqual(normalize_digits('(11) 98888-7777'), '11988887777')
        self.assertEqual(normalize_digits('123.456.789-00'), '12345678900')
        self.assertEqual(normalize_digits(None), '')
        self.assertEqual(normalize_digits(''), '')


class AcentosTests(AuditDuplicatesTestBase):
    def test_nomes_com_e_sem_acento_detectados_como_identicos(self):
        a = self.add_patient(name='João Silva')
        b = self.add_patient(name='Joao Silva')
        self.link(a, self.doctor1, 1001)
        self.link(b, self.doctor1, 1002)

        records = self.fetch_records()
        recs = self.dup_records_for(records, a.id, 'provável_duplicado')
        self.assertTrue(recs, 'acento deveria ser ignorado na comparação de nomes')
        self.assertEqual(recs[0]['risk'], 'alto')  # homônimos com o mesmo médico
        self.assertIn('Nomes idênticos', recs[0]['reason'])
        self.assertIn(b.id, recs[0]['related_ids'])


class DigitosTests(AuditDuplicatesTestBase):
    def test_telefone_formatado_agrupa_com_so_digitos(self):
        # Nomes totalmente diferentes: o par só pode nascer do grupo de
        # telefone. Mesma data de nascimento leva o score a 5 (alto).
        a = self.add_patient(name='Carlos Pereira', phone='11988887777',
                             birth_date=date(1980, 1, 1))
        b = self.add_patient(name='Roberto Gomes', phone='11988887777',
                             birth_date=date(1980, 1, 1))
        self.set_raw_phone(a.id, '(11) 98888-7777')  # legado formatado

        records = self.fetch_records()
        recs = self.dup_records_for(records, a.id, 'mesmo_telefone')
        self.assertTrue(recs, 'telefone formatado deveria agrupar com só dígitos')
        self.assertIn(b.id, recs[0]['related_ids'])

    def test_cpf_formatado_agrupa_com_so_digitos(self):
        a = self.add_patient(name='Ana Braga', cpf='12345678900')
        b = self.add_patient(name='Bruna Melo')
        self.set_raw_cpf(b.id, '123.456.789-00')  # legado formatado

        records = self.fetch_records()
        recs = self.dup_records_for(records, a.id, 'mesmo_cpf')
        self.assertTrue(recs, 'CPF formatado deveria agrupar com só dígitos')
        self.assertEqual(recs[0]['risk'], 'alto')  # mesmo CPF = +5
        self.assertIn(b.id, recs[0]['related_ids'])


class MedicosDistintosTests(AuditDuplicatesTestBase):
    def test_nomes_identicos_com_medicos_distintos_gera_risco_medio(self):
        a = self.add_patient(name='Pedro Alves')
        b = self.add_patient(name='Pedro Alves')
        self.link(a, self.doctor1, 1001)
        self.link(b, self.doctor2, 1001)

        records = self.fetch_records()
        recs = self.dup_records_for(records, a.id, 'provável_duplicado')
        self.assertTrue(recs, 'homônimos com médicos distintos não podem ser pulados')
        self.assertEqual(recs[0]['risk'], 'médio')
        self.assertEqual(recs[0]['reason'], 'Nomes idênticos (médicos distintos)')
        self.assertIn(b.id, recs[0]['related_ids'])


class ScoreCompostoTests(AuditDuplicatesTestBase):
    def test_mesmo_nome_com_birth_e_cpf_diferentes_nao_reporta(self):
        # Nome idêntico (+3), nascimentos diferentes (-2), CPFs diferentes
        # (-5): score -4 — evidência forte de que são pessoas distintas.
        a = self.add_patient(name='Maria Souza', birth_date=date(1980, 1, 1),
                             cpf='11111111111')
        b = self.add_patient(name='Maria Souza', birth_date=date(1990, 2, 2),
                             cpf='22222222222')

        records = self.fetch_records()
        self.assertFalse(self.dup_records_for(records, a.id))
        self.assertFalse(self.dup_records_for(records, b.id))

    def test_mesmo_nome_e_mesma_birth_date_reporta_risco_alto(self):
        # Nome idêntico (+3) e mesma data de nascimento (+3): score 6.
        a = self.add_patient(name='Lucia Ramos', birth_date=date(1975, 5, 5))
        b = self.add_patient(name='Lucia Ramos', birth_date=date(1975, 5, 5))

        records = self.fetch_records()
        recs = self.dup_records_for(records, a.id, 'provável_duplicado')
        self.assertTrue(recs)
        self.assertEqual(recs[0]['risk'], 'alto')
        self.assertGreaterEqual(recs[0]['score'], 5)
        self.assertIn('nome normalizado idêntico (+3)', recs[0]['evidence'])
        self.assertIn('mesma data de nascimento (+3)', recs[0]['evidence'])

    def test_cluster_de_tres_registros_em_related_ids(self):
        a = self.add_patient(name='Helena Costa', birth_date=date(1960, 3, 3))
        b = self.add_patient(name='Helena Costa', birth_date=date(1960, 3, 3))
        c = self.add_patient(name='Helena Costa', birth_date=date(1960, 3, 3))
        expected = sorted([a.id, b.id, c.id])

        records = self.fetch_records()
        for pid in expected:
            recs = self.dup_records_for(records, pid, 'provável_duplicado')
            self.assertTrue(recs, f'paciente {pid} deveria estar no cluster')
            self.assertEqual(sorted(recs[0]['related_ids']), expected)


if __name__ == '__main__':
    unittest.main()
