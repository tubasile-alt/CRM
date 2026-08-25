from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read_source(path):
    return (ROOT / path).read_text(encoding='utf-8')


def test_special_prescription_buttons_use_active_tab_state():
    source = read_source('static/js/dermascribe.js')

    assert 'function getActiveSpecialtyPrescriptionState()' in source
    assert 'return activeSpecialty.saveAndPrint(e);' in source
    assert 'return activeSpecialty.printPreview(e);' in source
    assert "window._specialtyPrescriptionStates[tabType]" in source


def test_special_prescription_notifies_parent_with_medication_lists():
    source = read_source('static/js/dermascribe.js')

    assert 'function notifyPrescriptionSaved(data, patientId, oral, topical, prescriptionType)' in source
    assert "notifyPrescriptionSaved(data, patient_id, savedOralMeds, savedTopMeds, tabType);" in source
    assert "notifyPrescriptionSaved(data, patient_id, savedMeds, [], tabType);" in source


def test_patient_photo_uses_no_store_and_secretary_can_edit():
    app_source = read_source('app.py')
    template = read_source('templates/prontuario.html')

    assert "'Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'" in app_source
    assert "can_edit_patient_photo = current_user.is_doctor() or current_user.is_secretary()" in template
    assert "photo_stamp" in template


def test_timeline_label_route_and_generic_dom_contract(flask_app):
    rules = {
        (rule.rule, tuple(sorted(rule.methods - {'HEAD', 'OPTIONS'})))
        for rule in flask_app.url_map.iter_rules()
    }
    template = read_source('templates/prontuario.html')
    js_source = read_source('static/js/prontuario.js')

    assert ('/api/timeline-events/label', ('PUT',)) in rules
    assert 'data-event-type="{{ first_event.label_event_type or first_event.type }}"' in template
    assert 'data-reference-id="{{ first_event.reference_id }}"' in template
    assert 'data-label-role="bubble"' in template
    assert 'data-label-role="title"' in template
    assert 'url: "/api/timeline-events/label"' in js_source
    assert 'syncTimelineTitleInstances' in js_source


def test_timeline_event_label_model_has_unique_event_reference():
    source = read_source('models.py')

    assert 'class TimelineEventLabel(db.Model):' in source
    assert "__tablename__ = 'timeline_event_label'" in source
    assert "db.UniqueConstraint('patient_id', 'event_type', 'reference_id'" in source


def test_timeline_dot_scrolls_to_consultation_history():
    template = read_source('templates/prontuario.html')
    js_source = read_source('static/js/prontuario.js')

    assert 'data-scroll-target="consultation-{{ scroll_consultation_id }}"' in template
    assert 'const scrollTarget = dot.getAttribute("data-scroll-target");' in js_source
    assert 'scrollToConsultation(scrollTarget);' in js_source


def test_consultation_history_has_visible_summary_contract():
    template = read_source('templates/prontuario.html')

    assert 'consultation-summary-toggle' in template
    assert 'history-preview-strip' in template
    assert "('Queixa', 'queixa'" in template
    assert "('Diagnóstico', 'diagnostico'" in template
    assert "('Conduta', 'conduta'" in template
    assert "asset_version('js/prontuario.js')" in template
