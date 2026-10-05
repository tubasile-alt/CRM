from app import _duplicate_override_is_confirmed


def test_duplicate_override_requires_confirmation_of_current_warning_ids():
    warnings = [{'id': 12}, {'id': 33}]

    assert _duplicate_override_is_confirmed(True, warnings, [12, 33])
    assert _duplicate_override_is_confirmed(True, warnings, [33, 12])
    assert not _duplicate_override_is_confirmed(True, warnings, [12])
    assert not _duplicate_override_is_confirmed(True, warnings, [12, 33, 48])
    assert not _duplicate_override_is_confirmed(False, warnings, [12, 33])


def test_duplicate_override_rejects_repeated_or_non_integer_ids():
    warnings = [{'id': 12}, {'id': 33}]

    assert not _duplicate_override_is_confirmed(True, warnings, [12, 12, 33])
    assert not _duplicate_override_is_confirmed(True, warnings, ['12', 33])
    assert not _duplicate_override_is_confirmed(True, warnings, [True, 33])
    assert not _duplicate_override_is_confirmed(True, warnings, None)
