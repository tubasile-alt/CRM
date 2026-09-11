import unittest
from datetime import datetime

from flask import Flask

from models import (
    CosmeticProcedurePlan,
    MessageDispatch,
    Note,
    Patient,
    ProcedureExecution,
    User,
    db,
)
from services.botox_sheet_service import build_botox_sheet_rows
from services.google_sheets import BOTOX_HEADERS


class BotoxSheetRowsTests(unittest.TestCase):
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
            doctor = User(
                username='doctor',
                email='doctor@example.com',
                password_hash='test',
                name='Doctor',
                role='medico',
            )
            patient = Patient(
                name='Paciente Botox',
                phone='(16) 99994-1774',
            )
            db.session.add_all([doctor, patient])
            db.session.flush()
            self.patient_id = patient.id
            note = Note(
                patient_id=patient.id,
                doctor_id=doctor.id,
                note_type='conduta',
                category='cosmiatria',
            )
            db.session.add(note)
            db.session.flush()
            self.note_id = note.id
            db.session.commit()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def _execution(
        self,
        procedure_name='Botox',
        status='realizada',
        performed_date=None,
    ):
        performed_date = performed_date or datetime(2026, 3, 10, 14, 30)
        plan = CosmeticProcedurePlan(
            note_id=self.note_id,
            name=procedure_name,
            procedure_name=procedure_name,
            follow_up_months=5,
        )
        db.session.add(plan)
        db.session.flush()
        execution = ProcedureExecution(
            plan_id=plan.id,
            execution_status=status,
            was_performed=status == 'realizada',
            performed_date=performed_date,
            followup_date=datetime(2026, 8, 10),
        )
        db.session.add(execution)
        db.session.flush()
        return execution

    def test_without_data_returns_only_header(self):
        with self.app.app_context():
            matrix = build_botox_sheet_rows()

        self.assertEqual(matrix, [list(BOTOX_HEADERS)])
        self.assertEqual(len(matrix[0]), 13)

    def test_realized_botox_without_dispatch_has_empty_status_columns(self):
        with self.app.app_context():
            execution = self._execution()
            db.session.commit()
            matrix = build_botox_sheet_rows()

            self.assertEqual(matrix[1][0], str(execution.id))
            self.assertEqual(matrix[1][5:], ['', '', '', '', '', '', '', ''])

    def test_d0_dispatch_is_rendered(self):
        with self.app.app_context():
            execution = self._execution()
            db.session.add(MessageDispatch(
                patient_id=self.patient_id,
                execution_id=execution.id,
                message_type='d0',
                due_at=datetime(2026, 3, 10).date(),
                status='enviada',
                sent_at=datetime(2026, 3, 10, 15, 45),
            ))
            db.session.commit()
            row = build_botox_sheet_rows()[1]

        self.assertEqual(row[5], 'enviada')
        self.assertEqual(row[6], 0)
        self.assertEqual(row[7], '')
        self.assertEqual(row[8], '10/03/2026 15:45')

    def test_non_botox_is_not_included(self):
        with self.app.app_context():
            self._execution(procedure_name='Sculptra')
            db.session.commit()
            matrix = build_botox_sheet_rows()

        self.assertEqual(len(matrix), 1)

    def test_scheduled_execution_is_not_included(self):
        with self.app.app_context():
            self._execution(status='agendada')
            db.session.commit()
            matrix = build_botox_sheet_rows()

        self.assertEqual(len(matrix), 1)

    def test_rows_are_ordered_by_performed_date(self):
        with self.app.app_context():
            later = self._execution(
                procedure_name='Botox face',
                performed_date=datetime(2026, 4, 20),
            )
            earlier = self._execution(
                procedure_name='Botox frontal',
                performed_date=datetime(2026, 2, 5),
            )
            db.session.commit()
            matrix = build_botox_sheet_rows()

            self.assertEqual(
                [matrix[1][0], matrix[2][0]],
                [str(earlier.id), str(later.id)],
            )

    def test_phone_is_formatted_for_sheets(self):
        with self.app.app_context():
            self._execution()
            db.session.commit()
            row = build_botox_sheet_rows()[1]

        self.assertEqual(row[2], '5516999941774')

    def test_same_patient_same_day_is_one_row_with_all_execution_ids(self):
        with self.app.app_context():
            first = self._execution(
                procedure_name='Botox glabela',
                performed_date=datetime(2026, 3, 10, 10, 0),
            )
            second = self._execution(
                procedure_name='Botox testa',
                performed_date=datetime(2026, 3, 10, 15, 0),
            )
            db.session.commit()

            matrix = build_botox_sheet_rows()

        self.assertEqual(len(matrix), 2)
        self.assertEqual(matrix[1][0], f'{first.id}, {second.id}')

    def test_dispatch_status_is_joined_by_patient_and_due_date(self):
        with self.app.app_context():
            first = self._execution(
                performed_date=datetime(2026, 3, 10, 10, 0),
            )
            self._execution(
                procedure_name='Botox testa',
                performed_date=datetime(2026, 3, 10, 15, 0),
            )
            db.session.add_all([
                MessageDispatch(
                    patient_id=self.patient_id,
                    execution_id=first.id,
                    message_type='d0',
                    due_at=datetime(2026, 3, 10).date(),
                    status='enviada',
                    sent_at=datetime(2026, 3, 10, 15, 45),
                ),
                MessageDispatch(
                    patient_id=self.patient_id,
                    execution_id=first.id,
                    message_type='m5',
                    due_at=datetime(2026, 8, 10).date(),
                    status='pendente',
                ),
            ])
            db.session.commit()

            row = build_botox_sheet_rows()[1]

        self.assertEqual(row[5], 'enviada')
        self.assertEqual(row[6], 0)
        self.assertEqual(row[7], '')
        self.assertEqual(row[8], '10/03/2026 15:45')
        self.assertEqual(row[9], 'pendente')
        self.assertEqual(row[10], 0)
        self.assertEqual(row[11], '')

    def test_pending_after_retry_shows_attempts_and_last_error(self):
        with self.app.app_context():
            execution = self._execution()
            db.session.add(MessageDispatch(
                patient_id=self.patient_id,
                execution_id=execution.id,
                message_type='d0',
                due_at=datetime(2026, 3, 11).date(),
                status='pendente',
                attempts=1,
                last_error='timeout',
            ))
            db.session.commit()
            row = build_botox_sheet_rows()[1]

        self.assertEqual(row[5], 'pendente')
        self.assertEqual(row[6], 1)
        self.assertEqual(row[7], 'timeout')
        self.assertEqual(row[8], '')

    def test_terminal_failure_is_marked_clearly(self):
        with self.app.app_context():
            execution = self._execution()
            db.session.add(MessageDispatch(
                patient_id=self.patient_id,
                execution_id=execution.id,
                message_type='m5',
                due_at=datetime(2026, 8, 10).date(),
                status='falhou',
                attempts=3,
                last_error='número recusado',
            ))
            db.session.commit()
            row = build_botox_sheet_rows()[1]

        self.assertEqual(row[9], 'falhou (terminal)')
        self.assertEqual(row[10], 3)
        self.assertEqual(row[11], 'número recusado')
        self.assertEqual(row[12], '')

    def test_grouped_dispatches_aggregate_attempts_and_errors(self):
        with self.app.app_context():
            first = self._execution(
                performed_date=datetime(2026, 3, 10, 10, 0),
            )
            second = self._execution(
                procedure_name='Botox testa',
                performed_date=datetime(2026, 3, 10, 15, 0),
            )
            db.session.add_all([
                MessageDispatch(
                    patient_id=self.patient_id,
                    execution_id=first.id,
                    message_type='d0',
                    due_at=datetime(2026, 3, 10).date(),
                    status='pendente',
                    attempts=1,
                    last_error='timeout',
                ),
                MessageDispatch(
                    patient_id=self.patient_id,
                    execution_id=second.id,
                    message_type='d0',
                    due_at=datetime(2026, 3, 11).date(),
                    status='pendente',
                    attempts=2,
                    last_error='número inválido',
                ),
            ])
            db.session.commit()

            matrix = build_botox_sheet_rows()

        self.assertEqual(len(matrix), 2)
        self.assertEqual(matrix[1][0], f'{first.id}, {second.id}')
        self.assertEqual(matrix[1][5], 'pendente')
        self.assertEqual(matrix[1][6], 3)
        self.assertEqual(matrix[1][7], 'timeout; número inválido')

    def test_grouped_dispatch_terminal_failure_overrides_sent_dispatch(self):
        with self.app.app_context():
            first = self._execution(
                performed_date=datetime(2026, 3, 10, 10, 0),
            )
            second = self._execution(
                procedure_name='Botox testa',
                performed_date=datetime(2026, 3, 10, 15, 0),
            )
            db.session.add_all([
                MessageDispatch(
                    patient_id=self.patient_id,
                    execution_id=first.id,
                    message_type='m5',
                    due_at=datetime(2026, 8, 10).date(),
                    status='enviada',
                    attempts=1,
                    sent_at=datetime(2026, 8, 10, 10, 0),
                ),
                MessageDispatch(
                    patient_id=self.patient_id,
                    execution_id=second.id,
                    message_type='m5',
                    due_at=datetime(2026, 8, 11).date(),
                    status='falhou',
                    attempts=3,
                    last_error='número recusado',
                ),
            ])
            db.session.commit()

            matrix = build_botox_sheet_rows()

        self.assertEqual(len(matrix), 2)
        self.assertEqual(matrix[1][0], f'{first.id}, {second.id}')
        self.assertEqual(matrix[1][9], 'falhou (terminal)')
        self.assertEqual(matrix[1][10], 4)
        self.assertEqual(matrix[1][11], 'número recusado')
        self.assertEqual(matrix[1][12], '10/08/2026 10:00')


if __name__ == '__main__':
    unittest.main()