import unittest

from flask import Flask

from models import Patient, db
from services.patient_identity import find_possible_duplicate_patients


class PatientIdentityTests(unittest.TestCase):
    def setUp(self):
        app = Flask(__name__)
        app.config.update(
            TESTING=True,
            SQLALCHEMY_DATABASE_URI='sqlite:///:memory:',
            SQLALCHEMY_TRACK_MODIFICATIONS=False,
        )
        db.init_app(app)
        self.app = app

        with app.app_context():
            db.create_all()
            patient = Patient(name='Claudia Data Legada')
            db.session.add(patient)
            db.session.flush()
            db.session.execute(
                db.text(
                    "UPDATE patient SET birth_date = '61969-03-25' WHERE id = :id"
                ),
                {'id': patient.id},
            )
            db.session.commit()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_duplicate_search_ignores_out_of_range_birth_date(self):
        with self.app.app_context():
            results = find_possible_duplicate_patients('Claudia Data Legada')

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['name'], 'Claudia Data Legada')
        self.assertIsNone(results[0]['birth_date'])


if __name__ == '__main__':
    unittest.main()