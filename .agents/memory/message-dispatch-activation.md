---
name: Message dispatch activation
description: Safety sequence for enabling automatic message-dispatch records.
---

Message-dispatch schema changes must run through the post-merge migration flow, not application startup. The message identity is `(patient_id, message_type, due_at)`, while `execution_id` remains the representative execution for traceability. Keep automatic listeners disabled by default until the target production database has the required table and patient consent column.

**Why:** Multiple Botox areas can create separate executions for one patient on one day; deduplicating by execution sends duplicate messages and duplicates spreadsheet rows. The app uses Autoscale, so startup DDL can delay health checks. Development and production may also point at different databases; enabling listeners before verifying the production schema could break procedure creation.

**How to apply:** After merge, verify the target schema, run the historical backfill as a dry run and review suppressed duplicates before any explicit commit, and only afterward enable the dispatch feature flag and restart the app. Rebuild the Botox sheet as one row per patient/date, storing all execution IDs in that row. Never treat a development-schema check as proof of production readiness.