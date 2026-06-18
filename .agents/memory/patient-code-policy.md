---
name: Patient code policy (FASE 1+)
description: How new patient_code generation/uniqueness works and why historical codes must never be touched.
---

# Patient code policy

`patient_code` lives in `patient_doctor` (per-doctor counter, not global). Historical codes are dirty: there is at least one same-doctor duplicate (doctor_id=5, code 264 → two patients) plus many duplicate-name patients. These were left intentionally untouched.

## New-code rule (from FASE 1)
- New codes start at **1001** per doctor. Generation rule: `next = max(max_code+1, 1001)`. Implemented in `generate_next_patient_code(doctor_id)` in `app.py`; all three creation call sites (create_appointment, CP prontuario redirect, link_doctor_patient) must use it — never inline `max+1`.

## Uniqueness — PARTIAL index, not a plain UNIQUE
- Enforcement is a PostgreSQL **partial** unique index: `UNIQUE(doctor_id, patient_code) WHERE patient_code >= 1001` (declared in `models.py` via `postgresql_where`, and created on the DB).
- **Why partial:** a normal `UNIQUE(doctor_id, patient_code)` is impossible to add while the historical duplicate 264 exists. The partial index enforces only the new range so all historical codes (incl. 264) survive. Do NOT replace it with a full unique constraint until FASE 2 cleans up historical duplicates.

## Concurrency
- Code generation takes `LOCK TABLE patient_doctor IN SHARE ROW EXCLUSIVE MODE` (guarded by `db.engine.dialect.name == 'postgresql'`) before reading max, so concurrent creators can't get the same code. Use `db.engine`, not `db.session.bind` (the latter is None outside a request).

## FASE 2 (pending, NOT done)
- Audit/fix historical duplicate codes (264), merge/dedupe duplicate-name patients. Strictly forbidden in FASE 1.
