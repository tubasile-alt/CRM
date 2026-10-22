from unittest.mock import patch

from flask_login import UserMixin
import pytest


class _AuthenticatedUser(UserMixin):
    id = 987654

    def get_id(self):
        return str(self.id)

    def is_doctor(self):
        return False


@pytest.fixture
def authenticated_client(flask_app):
    client = flask_app.test_client()
    with patch.object(flask_app.login_manager, "_user_callback", lambda user_id: _AuthenticatedUser()):
        with client.session_transaction() as session:
            session["_user_id"] = "987654"
            session["_fresh"] = True
        yield client


def test_notch_redirects_to_login_and_preserves_return_path(flask_app):
    response = flask_app.test_client().get("/espera/notch")

    assert response.status_code == 302
    assert response.headers["Location"].startswith("/login?")
    assert "next=%2Fespera%2Fnotch" in response.headers["Location"]


def test_notch_renders_for_authenticated_user(authenticated_client):
    response = authenticated_client.get("/espera/notch")

    assert response.status_code == 200
    assert "Sala de espera" in response.get_data(as_text=True)
    assert "/espera/api/list" in response.get_data(as_text=True)


def test_waiting_list_api_keeps_existing_response_shape(authenticated_client):
    expected_list = [{
        "appointment_id": 123,
        "id": 123,
        "patient_id": 456,
        "patient_name": "Paciente de teste",
        "scheduled_time": "15:30",
        "room": "Sala 1",
        "wait_time_minutes": 12,
    }]
    expected_stats = {"count": 1, "average_wait_minutes": 12}

    with patch("routes.waiting_room.waiting_service.get_waiting_list", return_value=expected_list), \
         patch("routes.waiting_room.waiting_service.get_wait_stats", return_value=expected_stats):
        response = authenticated_client.get("/espera/api/list")

    assert response.status_code == 200
    assert response.get_json() == {
        "waiting_list": expected_list,
        "stats": expected_stats,
    }
