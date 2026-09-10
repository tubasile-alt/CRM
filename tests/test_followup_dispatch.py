import unittest
from datetime import datetime, timedelta
from types import SimpleNamespace

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
from services.clinic_time import clinic_today
from services import followup_service
from services.followup_service import build_dispatch_rows, compute_m5_date


class FollowupDispatchTests(unittest.TestCase):
    def setUp(self):
        app = Flask(__name__)
        app.config.update(
            TESTING=True,
            SQLALCHEMY_DATABASE_URI='sqlite:///:memory:',
            SQLALCHEMY_TRACK_MODIFICATIONS=False,
        )
        db.init_app(app)
        self.app = app
        self.previous_enabled = followup_service.DISPATCH_ENABLED
        followup_service.DISPATCH_ENABLED = True

        with app.app_context():
            db.create_all()
            doctor = User(
                username='doctor',
                email='doctor@example.com',
                password_hash='test',
                name='Doctor',
                role='medico',
            )
            patient = Patient(name='Paciente Botox', phone='16999941774')
            db.session.add_all([doctor, patient])
            db.session.flush()
            note = Note(
                patient_id=patient.id,
                doctor_id=doctor.id,
                note_type='conduta',
                category='cosmiatria',
            )
            db.session.add(note)
            db.session.flush()
            self.botox_plan = CosmeticProcedurePlan(
                note_id=note.id,
                name='Botox',
                procedure_name='Botox',
                follow_up_months=5,
            )
            self.other_plan = CosmeticProcedurePlan(
                note_id=note.id,
                name='Sculptra',
                procedure_name='Sculptra',
                follow_up_months=18,
            )
            db.session.add_all([self.botox_plan, self.other_plan])
            db.session.commit()
            self.botox_plan_id = self.botox_plan.id
            self.other_plan_id = self.other_plan.id

    def tearDown(self):
        followup_service.DISPATCH_ENABLED = self.previous_enabled
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_build_dispatch_rows_today_creates_pending_d0_and_m5(self):
        today = clinic_today()
        execution = SimpleNamespace(
            id=10,
            execution_status='realizada',
            performed_date=datetime.combine(today, datetime.min.time()),
        )
        plan = SimpleNamespace(procedure_name='Botox')

        rows = build_dispatch_rows(execution, plan, today=today)

        self.assertEqual([row['message_type'] for row in rows], ['d0', 'm5'])
        self.assertEqual([row['status'] for row in rows], ['pendente', 'pendente'])
        self.assertEqual(rows[0]['due_at'], today)
        self.assertEqual(rows[1]['due_at'], compute_m5_date(execution.performed_date))

    def test_build_dispatch_rows_retroactive_skips_d0(self):
        today = clinic_today()
        execution = SimpleNamespace(
            id=11,
            execution_status='realizada',
            performed_date=datetime.combine(
                today - timedelta(days=10),
                datetime.min.time(),
            ),
        )
        plan = SimpleNamespace(procedure_name='Botox')

        rows = build_dispatch_rows(execution, plan, today=today)

        self.assertEqual(rows[0]['status'], 'pulada')
        self.assertEqual(rows[1]['status'], 'pendente')

    def test_direct_realized_execution_creates_two_dispatches(self):
        today = clinic_today()
        with self.app.app_context():
            execution = ProcedureExecution(
                plan_id=self.botox_plan_id,
                performed_date=datetime.combine(today, datetime.min.time()),
                execution_status='realizada',
                was_performed=True,
            )
            db.session.add(execution)
            db.session.commit()

            rows = MessageDispatch.query.filter_by(execution_id=execution.id).all()
            self.assertEqual(len(rows), 2)

    def test_transition_to_realized_creates_two_dispatches(self):
        today = clinic_today()
        with self.app.app_context():
            execution = ProcedureExecution(
                plan_id=self.botox_plan_id,
                scheduled_date=datetime.combine(today, datetime.min.time()),
                execution_status='agendada',
                was_performed=False,
            )
            db.session.add(execution)
            db.session.commit()
            self.assertEqual(MessageDispatch.query.count(), 0)

            execution.execution_status = 'realizada'
            execution.was_performed = True
            execution.performed_date = datetime.combine(today, datetime.min.time())
            db.session.commit()

            self.assertEqual(
                MessageDispatch.query.filter_by(execution_id=execution.id).count(),
                2,
            )

    def test_repeated_updates_do_not_duplicate_dispatches(self):
        today = clinic_today()
        with self.app.app_context():
            execution = ProcedureExecution(
                plan_id=self.botox_plan_id,
                scheduled_date=datetime.combine(today, datetime.min.time()),
                execution_status='agendada',
                was_performed=False,
            )
            db.session.add(execution)
            db.session.commit()

            execution.execution_status = 'realizada'
            execution.was_performed = True
            execution.performed_date = datetime.combine(today, datetime.min.time())
            db.session.commit()
            execution.notes = 'Primeira atualização'
            db.session.commit()
            execution.notes = 'Segunda atualização'
            db.session.commit()

            self.assertEqual(
                MessageDispatch.query.filter_by(execution_id=execution.id).count(),
                2,
            )

    def test_same_patient_same_day_creates_only_two_dispatches(self):
        today = clinic_today()
        with self.app.app_context():
            for hour in (10, 14):
                db.session.add(ProcedureExecution(
                    plan_id=self.botox_plan_id,
                    performed_date=datetime.combine(
                        today,
                        datetime.min.time().replace(hour=hour),
                    ),
                    execution_status='realizada',
                    was_performed=True,
                ))
            db.session.commit()

            self.assertEqual(MessageDispatch.query.count(), 2)
            self.assertEqual(
                {dispatch.message_type for dispatch in MessageDispatch.query.all()},
                {'d0', 'm5'},
            )

    def test_same_patient_on_different_days_creates_four_dispatches(self):
        today = clinic_today()
        with self.app.app_context():
            for day in (today - timedelta(days=1), today):
                db.session.add(ProcedureExecution(
                    plan_id=self.botox_plan_id,
                    performed_date=datetime.combine(day, datetime.min.time()),
                    execution_status='realizada',
                    was_performed=True,
                ))
            db.session.commit()

            self.assertEqual(MessageDispatch.query.count(), 4)

    def test_non_botox_execution_creates_no_dispatches(self):
        today = clinic_today()
        with self.app.app_context():
            execution = ProcedureExecution(
                plan_id=self.other_plan_id,
                performed_date=datetime.combine(today, datetime.min.time()),
                execution_status='realizada',
                was_performed=True,
            )
            db.session.add(execution)
            db.session.commit()

            self.assertEqual(MessageDispatch.query.count(), 0)

    def test_followup_date_is_filled_on_realized_transition(self):
        today = clinic_today()
        with self.app.app_context():
            execution = ProcedureExecution(
                plan_id=self.botox_plan_id,
                scheduled_date=datetime.combine(today, datetime.min.time()),
                execution_status='agendada',
                was_performed=False,
            )
            db.session.add(execution)
            db.session.commit()

            execution.execution_status = 'realizada'
            execution.was_performed = True
            execution.performed_date = datetime.combine(today, datetime.min.time())
            db.session.commit()

            self.assertEqual(
                execution.followup_date.date(),
                compute_m5_date(execution.performed_date),
            )


if __name__ == '__main__':
    unittest.main()