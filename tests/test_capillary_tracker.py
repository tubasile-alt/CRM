import json
import urllib.parse
from types import SimpleNamespace

import pytest
from werkzeug.exceptions import Forbidden

from services import capillary_tracker


def test_normalize_name_removes_accents_punctuation_and_extra_spaces():
    assert capillary_tracker.normalize_name("  João da Silva, Jr. ") == "joao da silva jr"


def test_config_requires_credentials_and_https(monkeypatch):
    monkeypatch.delenv("TRACKER_API_URL", raising=False)
    monkeypatch.delenv("TRACKER_API_KEY", raising=False)
    with pytest.raises(capillary_tracker.TrackerNotConfigured):
        capillary_tracker._config()

    monkeypatch.setenv("TRACKER_API_URL", "http://tracker.example")
    monkeypatch.setenv("TRACKER_API_KEY", "test-key")
    with pytest.raises(capillary_tracker.TrackerNotConfigured):
        capillary_tracker._config()

    monkeypatch.setenv("TRACKER_API_URL", "https://tracker.example/")
    assert capillary_tracker._config() == ("https://tracker.example", "test-key")


def test_fetch_candidates_uses_tracker_read_only_endpoint_and_api_key(monkeypatch):
    monkeypatch.setenv("TRACKER_API_URL", "https://tracker.example/")
    monkeypatch.setenv("TRACKER_API_KEY", "test-key")
    captured = {}

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def read(self):
            return json.dumps({"matches": [{"nome": "Maria Silva"}]}).encode()

    def fake_urlopen(request, timeout):
        captured["request"] = request
        captured["timeout"] = timeout
        return FakeResponse()

    monkeypatch.setattr(capillary_tracker.urllib.request, "urlopen", fake_urlopen)

    matches = capillary_tracker._fetch_candidates("Maria Silva")

    request = captured["request"]
    parsed_url = urllib.parse.urlparse(request.full_url)
    assert parsed_url.path == "/api/integracao/cirurgias"
    assert urllib.parse.parse_qs(parsed_url.query) == {"nome": ["Maria Silva"]}
    assert request.get_header("X-api-key") == "test-key"
    assert request.get_header("Accept") == "application/json"
    assert captured["timeout"] == capillary_tracker.TIMEOUT_SECONDS
    assert matches == [{"nome": "Maria Silva"}]


def test_search_by_name_scores_filters_and_sorts_candidates(monkeypatch):
    candidates = [
        {"nome": "Maria Souza Silva", "data": "2025-01-01"},
        {"nome": "Maria Silva", "data": "2024-01-01"},
        {"nome": "Alice Jones", "data": "2026-01-01"},
    ]
    monkeypatch.setattr(
        capillary_tracker,
        "_fetch_candidates",
        lambda _name: candidates,
    )

    results = capillary_tracker.search_by_name("María Silva")

    assert [item["nome"] for item in results] == [
        "Maria Silva",
        "Maria Souza Silva",
    ]
    assert results[0]["match_score"] == 1.0
    assert results[0]["match_label"] == "exato"
    assert results[1]["match_label"] == "provavel"
    assert results[0]["necroses"] == []


def test_search_by_name_skips_names_without_searchable_tokens(monkeypatch):
    def should_not_fetch(_name):
        raise AssertionError("A busca não deve chamar o Tracker para nomes curtos.")

    monkeypatch.setattr(capillary_tracker, "_fetch_candidates", should_not_fetch)

    assert capillary_tracker.search_by_name("A") == []


def test_tracker_route_returns_read_only_matches_for_assigned_doctor(
    monkeypatch, flask_app
):
    from routes import patient as patient_routes

    patient = SimpleNamespace(name="Maria Silva")

    class PatientQuery:
        @staticmethod
        def get_or_404(_patient_id):
            return patient

    class FakePatient:
        query = PatientQuery()

    class PatientDoctorQuery:
        def filter_by(self, **_filters):
            return self

        @staticmethod
        def first():
            return object()

    class FakePatientDoctor:
        query = PatientDoctorQuery()

    user = SimpleNamespace(
        id=7,
        is_admin=lambda: False,
        is_secretary=lambda: False,
        is_doctor=lambda: True,
    )
    matches = [{"nome": "Maria Silva", "match_score": 1.0}]
    searched_names = []

    monkeypatch.setattr(patient_routes, "Patient", FakePatient)
    monkeypatch.setattr(patient_routes, "PatientDoctor", FakePatientDoctor)
    monkeypatch.setattr(patient_routes, "current_user", user)
    monkeypatch.setattr(
        capillary_tracker,
        "search_by_name",
        lambda name: searched_names.append(name) or matches,
    )

    with flask_app.test_request_context():
        response = patient_routes.get_tracker_surgeries.__wrapped__(42)

    assert response.status_code == 200
    assert response.get_json() == {
        "success": True,
        "source": "CapillaryTracker",
        "read_only": True,
        "matches": matches,
    }
    assert response.headers["Cache-Control"] == "no-store"
    assert searched_names == ["Maria Silva"]


def test_tracker_route_rejects_doctors_without_patient_access(
    monkeypatch, flask_app
):
    from routes import patient as patient_routes

    class PatientQuery:
        @staticmethod
        def get_or_404(_patient_id):
            return SimpleNamespace(name="Maria Silva")

    class FakePatient:
        query = PatientQuery()

    class PatientDoctorQuery:
        def filter_by(self, **_filters):
            return self

        @staticmethod
        def first():
            return None

    class FakePatientDoctor:
        query = PatientDoctorQuery()

    user = SimpleNamespace(
        id=7,
        is_admin=lambda: False,
        is_secretary=lambda: False,
        is_doctor=lambda: True,
    )
    monkeypatch.setattr(patient_routes, "Patient", FakePatient)
    monkeypatch.setattr(patient_routes, "PatientDoctor", FakePatientDoctor)
    monkeypatch.setattr(patient_routes, "current_user", user)

    with flask_app.test_request_context(), pytest.raises(Forbidden):
        patient_routes.get_tracker_surgeries.__wrapped__(42)
