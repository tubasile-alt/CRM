---
name: Message dispatch activation
description: Safety sequence for enabling automatic message-dispatch records.
---

Message-dispatch schema changes must run through the post-merge migration flow, not application startup. The message identity is `(patient_id, message_type, due_at)`, while `execution_id` remains the representative execution for traceability. External delivery also requires API key, explicit send mode, and daily cap; all default off.

**Why:** Multiple Botox areas can create separate executions for one patient on one day; deduplicating by execution sends duplicate messages and duplicates spreadsheet rows. Delivery needs independent fail-closed controls so an integration cannot send while only partially configured. The app uses Autoscale, so startup DDL can delay health checks. Development and production may also point at different databases; enabling listeners before verifying the production schema could break procedure creation.

**How to apply:** After merge, verify the target schema, run the historical backfill as a dry run and review suppressed duplicates before any explicit commit, and only afterward enable the dispatch feature flag and restart the app. Rebuild the Botox sheet as one row per patient/date, storing all execution IDs in that row. Keep integration secrets absent until an intentional activation plan is approved. Never treat a development-schema check as proof of production readiness.