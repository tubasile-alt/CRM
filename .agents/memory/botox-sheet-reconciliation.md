---
name: Botox sheet reconciliation
description: Reliability and activation rules for the shared Botox Google Sheet mirror.
---

Treat the Botox worksheet as a full database mirror rebuilt by reconciliation, never as an append-only request side effect. The Preview and production app share this worksheet.

**Why:** Daemon-thread appends silently lost rows, and an Autoscale container may stop before an in-process interval scheduler runs. A full rewrite is recoverable and idempotent, but the first execution replaces real shared data.

**How to apply:** Keep manual sync as the reliable Phase 2 trigger and regard the six-hour scheduler as best-effort only. Before the first real sync, require a manually duplicated worksheet backup and verify the dry-run count. Use an external guaranteed trigger in a later phase.

Dispatch metadata must be matched to the stable procedure execution and message type, not to `due_at`, because a failed delivery changes its due date during retry backoff.

**Why:** A retry would otherwise disappear from the sheet even though the dispatch still exists in the database.

**How to apply:** Keep reconciliation keyed by execution identity when displaying status, attempts, errors, or terminal failures.