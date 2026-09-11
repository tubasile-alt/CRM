from datetime import datetime

import pytest
from flask import Flask

from models import (
    CosmeticProcedurePlan,
    MessageDispatch,
    MessageDispatchStatusAudit,
    Note,
    Patient,
    ProcedureExecution,
    User,
    db,
)
from routes.integrations import integrations_bp
from services.message_dispatch_status import list_unknown_dispatches


@pytest.fixture
def repair_client(monkeypatch):
    app = Flask(__name__)
    app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI='sqlite:///:memory:',
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )
    db.init_app(app)
    app.register_blueprint(integrations_bp)
    monkeypatch.setenv('INTEGRATIONS_API_KEY', 'expected')

    with app.app_context():
        db.create_all()
        doctor = User(
            username='doctor',
            email='doctor@example.com',
            password_hash='test',
            name='Doctor',
            role='medico',
        )
        patient = Patient(name='Paciente para revisão', phone='5516999941774')
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
        plan = CosmeticProcedurePlan(
            note_id=note.id,
            name='Botox',
            procedure_name='Botox',
            follow_up_months=5,
        )
        db.session.add(plan)
        db.session.flush()
        execution = ProcedureExecution(
            plan_id=plan.id,
            execution_status='realizada',
            was_performed=True,
            performed_date=datetime(2026, 9, 1, 10, 0),
        )
        db.session.add(execution)
        db.session.flush()
        unknown = MessageDispatch(
            patient_id=patient.id,
            execution_id=execution.id,
            message_type='m5',
            due_at=datetime(2026, 9, 1).date(),
            status='estado_novo',
            attempts=1,
            last_error='resposta inesperada',
        )
        terminal = MessageDispatch(
            patient_id=patient.id,
            execution_id=execution.id,
            message_type='d0',
            due_at=datetime(2026, 9, 1).date(),
            status='falhou',
            attempts=3,
            last_error='falha permanente',
        )
        db.session.add_all([unknown, terminal])
        db.session.commit()
        yield app.test_client(), unknown.id, terminal.id
        db.session.remove()
        db.drop_all()


def test_unknown_report_is_read_only_and_excludes_terminal_failures(
    repair_client,
):
    client, unknown_id, terminal_id = repair_client

    response = client.get(
        '/api/integrations/messages/unknown-status',
        headers={'X-API-Key': 'expected'},
    )

    assert response.status_code == 200
    assert response.json['total'] == 1
    item = response.json['dispatches'][0]
    assert item['dispatch_id'] == unknown_id
    assert item['status'] == 'estado_novo'
    assert item['patient_name'] == 'Paciente para revisão'
    assert item['execution_id'] is not None
    assert terminal_id not in [row['dispatch_id'] for row in response.json['dispatches']]


def test_status_correction_is_explicit_audited_and_idempotent(repair_client):
    client, unknown_id, _terminal_id = repair_client

    first = client.patch(
        f'/api/integrations/messages/{unknown_id}/status-correction',
        headers={'X-API-Key': 'expected'},
        json={
            'target_status': 'pendente',
            'actor': 'operacao',
            'reason': 'estado confirmado na revisão',
        },
    )
    second = client.patch(
        f'/api/integrations/messages/{unknown_id}/status-correction',
        headers={'X-API-Key': 'expected'},
        json={'target_status': 'enviada'},
    )

    assert first.status_code == 200
    assert first.json['changed'] is True
    assert first.json['status'] == 'pendente'
    assert first.json['audit_id'] == 1
    assert second.status_code == 200
    assert second.json['changed'] is False
    assert second.json['status'] == 'pendente'

    with client.application.app_context():
        audit = MessageDispatchStatusAudit.query.one()
        assert audit.dispatch_id == unknown_id
        assert audit.previous_status == 'estado_novo'
        assert audit.new_status == 'pendente'
        assert audit.actor == 'operacao'
        assert audit.reason == 'estado confirmado na revisão'
        assert list_unknown_dispatches()['dispatches'] == []


def test_status_correction_rejects_unknown_target_and_does_not_change_terminal(
    repair_client,
):
    client, unknown_id, terminal_id = repair_client

    invalid = client.patch(
        f'/api/integrations/messages/{unknown_id}/status-correction',
        headers={'X-API-Key': 'expected'},
        json={'target_status': 'desconhecido'},
    )
    terminal = client.patch(
        f'/api/integrations/messages/{terminal_id}/status-correction',
        headers={'X-API-Key': 'expected'},
        json={'target_status': 'pendente'},
    )

    assert invalid.status_code == 400
    assert terminal.status_code == 200
    assert terminal.json['changed'] is False
    assert terminal.json['status'] == 'falhou'

    with client.application.app_context():
        assert MessageDispatchStatusAudit.query.count() == 0
        assert db.session.get(MessageDispatch, terminal_id).status == 'falhou'