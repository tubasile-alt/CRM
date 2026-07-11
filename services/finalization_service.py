"""Shared helpers extracted from app.py without behavior changes."""

def _note_counts_as_finalized(note):
    if not note:
        return False

    if getattr(note, 'is_finalized', False):
        return True

    if getattr(note, 'finalized_at', None):
        return True

    duration = getattr(note, 'consultation_duration', None)
    if duration is not None:
        return True

    return False

def _find_finalized_note(notes):
    if not notes:
        return None

    explicit_note = next((n for n in notes if _note_counts_as_finalized(n)), None)
    if explicit_note:
        return explicit_note

    return next((
        n for n in notes
        if n.note_type == 'conduta' and (
            (n.content or '').strip() == '[Conduta registrada via procedimentos]'
            or len(getattr(n, 'indications', []) or []) > 0
            or len(getattr(n, 'cosmetic_plans', []) or []) > 0
            or len(getattr(n, 'hair_transplants', []) or []) > 0
        )
    ), None)

def _resolve_consultation_finalization(appointment, grouped_notes):
    finalized_note = _find_finalized_note(grouped_notes)
    appointment_finalized = bool(
        appointment and (
            getattr(appointment, 'is_finalized', False)
            or getattr(appointment, 'finalized_at', None)
        )
    )
    return appointment_finalized or finalized_note is not None, finalized_note
