from datetime import date
from types import SimpleNamespace

import pytest
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
from routes import integrations


class FakeQuery:
    def __init__(self, rows):
        self.rows = rows

    def all(self):
        return list(self.rows)


def fake_row(dispatch_id, phone, message_type='m5', status='pendente'):
    dispatch = SimpleNamespace(
        id=dispatch_id,
        message_type=message_type,
        execution_id=dispatch_id + 1000,
        due_at=date(2026, 9, 1),
        status=status,
        sent_at=None,
    )
    patient = SimpleNamespace(
        id=dispatch_id + 2000,
        name=f'Paciente {dispatch_id}',
        phone=phone,
    )
    return dispatch, patient


@pytest.fixture
def integration_client(flask_app):
    return flask_app.test_client()


def test_without_api_key_all_routes_return_503(
    integration_client,
    monkeypatch,
):
    monkeypatch.delenv('INTEGRATIONS_API_KEY', raising=False)

    for method, path in (
        ('get', '/api/integrations/messages/due'),
        ('get', '/api/integrations/messages/preview'),
        ('patch', '/api/integrations/messages/1'),
        ('post', '/api/integrations/botox-sheet/sync'),
    ):
        response = getattr(integration_client, method)(path)
        assert response.status_code == 503


def test_wrong_api_key_returns_401(integration_client, monkeypatch):
    monkeypatch.setenv('INTEGRATIONS_API_KEY', 'expected')

    response = integration_client.get(
        '/api/integrations/messages/due',
        headers={'X-API-Key': 'wrong'},
    )

    assert response.status_code == 401


def test_due_is_silent_when_send_mode_is_absent(
    integration_client,
    monkeypatch,
):
    monkeypatch.setenv('INTEGRATIONS_API_KEY', 'expected')
    monkeypatch.delenv('DISPATCH_SEND_MODE', raising=False)

    with monkeypatch.context() as context:
        context.setattr(
            integrations,
            '_pending_query',
            lambda: (_ for _ in ()).throw(
                AssertionError('off não deve consultar a fila')
            ),
        )
        response = integration_client.get(
            '/api/integrations/messages/due',
            headers={'X-API-Key': 'expected'},
        )

    assert response.status_code == 200
    assert response.json['messages'] == []
    assert response.json['mode'] == 'off'


def test_test_mode_without_test_phone_is_empty(
    integration_client,
    monkeypatch,
):
    monkeypatch.setenv('INTEGRATIONS_API_KEY', 'expected')
    monkeypatch.setenv('DISPATCH_SEND_MODE', 'test')
    monkeypatch.delenv('DISPATCH_TEST_PHONES', raising=False)
    monkeypatch.setattr(
        integrations,
        '_pending_query',
        lambda: FakeQuery([fake_row(1, '5516999941774')]),
    )
    monkeypatch.setattr(integrations, '_sent_today', lambda: 0)

    response = integration_client.get(
        '/api/integrations/messages/due',
        headers={'X-API-Key': 'expected'},
    )

    assert response.status_code == 200
    assert response.json['messages'] == []


def test_test_mode_only_releases_configured_phone(
    integration_client,
    monkeypatch,
):
    monkeypatch.setenv('INTEGRATIONS_API_KEY', 'expected')
    monkeypatch.setenv('DISPATCH_SEND_MODE', 'test')
    monkeypatch.setenv('DISPATCH_TEST_PHONES', '16999941774')
    monkeypatch.setattr(
        integrations,
        '_pending_query',
        lambda: FakeQuery([
            fake_row(1, '5516999941774'),
            fake_row(2, '5516999000000'),
        ]),
    )
    monkeypatch.setattr(integrations, '_sent_today', lambda: 0)

    response = integration_client.get(
        '/api/integrations/messages/due',
        headers={'X-API-Key': 'expected'},
    )

    assert response.status_code == 200
    assert [item['dispatch_id'] for item in response.json['messages']] == [1]


def test_live_mode_enforces_daily_cap(
    integration_client,
    monkeypatch,
):
    monkeypatch.setenv('INTEGRATIONS_API_KEY', 'expected')
    monkeypatch.setenv('DISPATCH_SEND_MODE', 'live')
    monkeypatch.setenv('DISPATCH_DAILY_CAP', '2')
    monkeypatch.setattr(
        integrations,
        '_pending_query',
        lambda: FakeQuery([fake_row(index, '5516999941774')
                           for index in range(1, 6)]),
    )
    monkeypatch.setattr(integrations, '_sent_today', lambda: 0)

    response = integration_client.get(
        '/api/integrations/messages/due?limit=50',
        headers={'X-API-Key': 'expected'},
    )

    assert response.status_code == 200
    assert len(response.json['messages']) == 2
    assert response.json['daily_cap'] == 2


def test_already_consumed_cap_returns_empty(
    integration_client,
    monkeypatch,
):
    monkeypatch.setenv('INTEGRATIONS_API_KEY', 'expected')
    monkeypatch.setenv('DISPATCH_SEND_MODE', 'live')
    monkeypatch.setenv('DISPATCH_DAILY_CAP', '2')
    monkeypatch.setattr(integrations, '_sent_today', lambda: 2)
    monkeypatch.setattr(
        integrations,
        '_pending_query',
        lambda: (_ for _ in ()).throw(
            AssertionError('cap atingido não deve consultar a fila')
        ),
    )

    response = integration_client.get(
        '/api/integrations/messages/due',
        headers={'X-API-Key': 'expected'},
    )

    assert response.status_code == 200
    assert response.json['messages'] == []
    assert 'cap diário atingido' in response.json['note']


def test_preview_ignores_mode_and_does_not_change_status(
    integration_client,
    monkeypatch,
):
    dispatch, patient = fake_row(1, '5516999941774')
    monkeypatch.setenv('INTEGRATIONS_API_KEY', 'expected')
    monkeypatch.setenv('DISPATCH_SEND_MODE', 'off')
    monkeypatch.setattr(
        integrations,
        '_pending_query',
        lambda: FakeQuery([(dispatch, patient)]),
    )
    monkeypatch.setattr(integrations, '_sent_today', lambda: 0)

    response = integration_client.get(
        '/api/integrations/messages/preview',
        headers={'X-API-Key': 'expected'},
    )

    assert response.status_code == 200
    assert response.json['mode_atual'] == 'off'
    assert response.json['total_vencidos'] == 1
    assert response.json['por_tipo'] == {'m5': 1}
    assert dispatch.status == 'pendente'


def test_patch_invalid_status_returns_400(integration_client, monkeypatch):
    monkeypatch.setenv('INTEGRATIONS_API_KEY', 'expected')

    response = integration_client.patch(
        '/api/integrations/messages/1',
        headers={'X-API-Key': 'expected'},
        json={'status': 'enviado'},
    )

    assert response.status_code == 400


def test_patch_missing_dispatch_returns_404(integration_client, monkeypatch):
    monkeypatch.setenv('INTEGRATIONS_API_KEY', 'expected')

    response = integration_client.patch(
        '/api/integrations/messages/999999',
        headers={'X-API-Key': 'expected'},
        json={'status': 'falhou'},
    )

    assert response.status_code == 404


def test_patch_updates_and_is_idempotent(monkeypatch):
    test_app = Flask(__name__)
    test_app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI='sqlite:///:memory:',
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )
    db.init_app(test_app)
    test_app.register_blueprint(integrations.integrations_bp)

    with test_app.app_context():
        db.create_all()
        doctor = User(
            username='integration-doctor',
            email='integration-doctor@example.com',
            password_hash='test',
            name='Doctor',
            role='medico',
        )
        patient = Patient(
            name='Paciente Integração',
            phone='16999941774',
            accepts_marketing=True,
        )
        db.session.add_all([doctor, patient])
        db.session.flush()
        note = Note(
            patient_id=patient.id,
            doctor_id=doctor.id,
            note_type='conduta',
        )
        db.session.add(note)
        db.session.flush()
        plan = CosmeticProcedurePlan(
            note_id=note.id,
            name='Botox',
            procedure_name='Botox',
        )
        db.session.add(plan)
        db.session.flush()
        execution = ProcedureExecution(
            plan_id=plan.id,
            execution_status='realizada',
            was_performed=True,
        )
        db.session.add(execution)
        db.session.flush()
        dispatch = MessageDispatch(
            patient_id=patient.id,
            execution_id=execution.id,
            message_type='m5',
            due_at=date(2026, 9, 1),
            status='pendente',
        )
        db.session.add(dispatch)
        db.session.commit()
        dispatch_id = dispatch.id

        client = test_app.test_client()
        with pytest.MonkeyPatch.context() as patch:
            patch.setenv('INTEGRATIONS_API_KEY', 'expected')
            first = client.patch(
                f'/api/integrations/messages/{dispatch_id}',
                headers={'X-API-Key': 'expected'},
                json={'status': 'enviada'},
            )
            assert first.status_code == 200
            assert first.json['status'] == 'enviada'

            db.session.expire_all()
            updated = db.session.get(MessageDispatch, dispatch_id)
            sent_at = updated.sent_at
            assert sent_at is not None

            second = client.patch(
                f'/api/integrations/messages/{dispatch_id}',
                headers={'X-API-Key': 'expected'},
                json={'status': 'falhou', 'error': 'não deve sobrescrever'},
            )
            assert second.status_code == 200
            assert second.json['status'] == 'enviada'

            db.session.expire_all()
            unchanged = db.session.get(MessageDispatch, dispatch_id)
            assert unchanged.status == 'enviada'
            assert unchanged.sent_at == sent_at

        db.drop_all()


def test_botox_sync_route_returns_service_result(
    integration_client,
    monkeypatch,
):
    monkeypatch.setenv('INTEGRATIONS_API_KEY', 'expected')
    monkeypatch.setattr(
        'services.botox_sheet_service.run_botox_sheet_sync',
        lambda: (True, 'ok'),
    )

    response = integration_client.post(
        '/api/integrations/botox-sheet/sync',
        headers={'X-API-Key': 'expected'},
    )

    assert response.status_code == 200
    assert response.json == {'ok': True, 'message': 'ok'}