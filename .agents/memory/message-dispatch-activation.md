---
name: Message dispatch activation
description: Safety sequence for enabling automatic message-dispatch records.
---

Message-dispatch schema changes must run through the post-merge migration flow, not application startup. Keep automatic listeners disabled by default until the target production database has the required table and patient consent column.

**Why:** The app uses Autoscale, so startup DDL can delay health checks. Development and production may also point at different databases; enabling listeners before verifying the production schema could break procedure creation.

**How to apply:** After merge, verify the production schema, run the historical backfill first as a dry run and then explicitly commit it, and only afterward enable the dispatch feature flag and restart the app. Never treat a development-schema check as proof of production readiness.