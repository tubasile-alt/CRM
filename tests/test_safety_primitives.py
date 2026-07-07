import unittest
import re
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace

from services.access_control import can_manage_owned_record, is_admin_user
from services.clinic_time import (
    CLINIC_TIMEZONE_NAME,
    clinic_now,
    clinic_wall_time_iso,
    utc_instant_to_clinic_iso,
)
from services.statuses import (
    AppointmentStatus,
    appointment_pending_status_values,
    normalize_appointment_status,
)


ROOT = Path(__file__).resolve().parents[1]


class AccessControlTests(unittest.TestCase):
    def user(self, user_id=1, role='medico', role_clinico='DERM', authenticated=True):
        return SimpleNamespace(
            id=user_id,
            role=role,
            role_clinico=role_clinico,
            is_authenticated=authenticated,
        )

    def test_admin_is_recognized_from_clinical_role(self):
        self.assertTrue(is_admin_user(self.user(role_clinico=' admin ')))

    def test_admin_is_recognized_from_legacy_role(self):
        self.assertTrue(is_admin_user(self.user(role='admin')))

    def test_owner_can_manage_own_record(self):
        self.assertTrue(can_manage_owned_record(self.user(user_id=7), owner_id=7))

    def test_other_doctor_cannot_manage_record(self):
        self.assertFalse(can_manage_owned_record(self.user(user_id=7), owner_id=8))

    def test_admin_can_manage_record_from_another_owner(self):
        self.assertTrue(can_manage_owned_record(self.user(user_id=7, role_clinico='ADMIN'), owner_id=8))

    def test_unauthenticated_user_cannot_manage_record(self):
        self.assertFalse(can_manage_owned_record(self.user(authenticated=False), owner_id=1))


class ClinicTimeTests(unittest.TestCase):
    def test_clinic_timezone_is_sao_paulo(self):
        self.assertEqual(getattr(clinic_now().tzinfo, 'key', None), CLINIC_TIMEZONE_NAME)

    def test_wall_time_keeps_appointment_clock_time(self):
        value = datetime(2026, 6, 29, 9, 30)
        self.assertEqual(clinic_wall_time_iso(value), '2026-06-29T09:30:00-03:00')

    def test_utc_checkin_is_serialized_in_sao_paulo(self):
        value = datetime(2026, 6, 29, 15, 0, tzinfo=timezone.utc)
        self.assertEqual(utc_instant_to_clinic_iso(value), '2026-06-29T12:00:00-03:00')

    def test_legacy_naive_checkin_is_interpreted_as_utc(self):
        value = datetime(2026, 6, 29, 15, 0)
        self.assertEqual(utc_instant_to_clinic_iso(value), '2026-06-29T12:00:00-03:00')


class StatusTests(unittest.TestCase):
    def test_feminine_legacy_aliases_are_normalized(self):
        self.assertEqual(normalize_appointment_status(' Agendada '), AppointmentStatus.SCHEDULED)
        self.assertEqual(normalize_appointment_status('CONFIRMADA'), AppointmentStatus.CONFIRMED)

    def test_unknown_status_is_preserved_for_compatibility(self):
        self.assertEqual(normalize_appointment_status('em_avaliacao'), 'em_avaliacao')

    def test_no_show_eligible_values_do_not_include_closed_states(self):
        values = appointment_pending_status_values(include_aliases=True)
        self.assertEqual(values, frozenset({'agendado', 'agendada', 'confirmado', 'confirmada'}))
        self.assertNotIn(AppointmentStatus.COMPLETED, values)
        self.assertNotIn(AppointmentStatus.NO_SHOW, values)


class AppointmentDeletionSafetyTests(unittest.TestCase):
    def test_physical_agenda_log_backref_uses_passive_deletes(self):
        source = (ROOT / 'models.py').read_text(encoding='utf-8')
        self.assertIn(
            "backref=db.backref('physical_import_log', uselist=False, passive_deletes=True)",
            source,
        )
        self.assertNotIn("passive_deletes=True,\n    )\n    doctor = db.relationship", source)

    def test_only_one_delete_appointment_route_is_registered_in_app_source(self):
        source = (ROOT / 'app.py').read_text(encoding='utf-8')
        routes = re.findall(r"@app\.route\('/api/appointments/<int:[^>]+>', methods=\['DELETE'\]\)", source)
        self.assertEqual(len(routes), 1)
        self.assertEqual(
            source.count("@app.route('/api/appointments/<int:appointment_id>', methods=['DELETE'])"),
            1,
        )
        self.assertNotIn("@app.route('/api/appointments/<int:id>', methods=['DELETE'])", source)


if __name__ == '__main__':
    unittest.main()
