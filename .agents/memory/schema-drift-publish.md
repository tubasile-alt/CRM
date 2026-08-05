---
name: Production schema drift
description: Publish can propose destructive drops when development lost tables that still exist in production.
---

When a publish diff proposes dropping production tables that are still part of the application's models, align the development schema by recreating the missing structures before publishing; the final diff should contain no table removals. Never run schema DDL from a request hook or deployment startup.

**Why:** Development lacked the photo and timeline-label tables while production still held data, causing a misleading destructive publish warning. Request-time DDL later blocked the Autoscale health check and caused a failed publish.

**How to apply:** Compare both schemas read-only, recreate only missing development structures from the model/production shape, then recalculate the publish diff and inspect every remaining statement. Keep `/health` and `/` free of migrations; apply schema changes through the development post-merge flow and Publish.