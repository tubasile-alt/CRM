---
name: Physical agenda confirmation
description: Physical agenda imports must validate the exact edited rows immediately before the explicit confirmation and write.
---

The physical agenda flow should prevalidate the final browser payload on both client and server immediately before creating appointments, and static assets must use a changing version rather than a fixed cache key.

**Why:** A reviewed table can diverge from the original AI result, while a stale JavaScript bundle can omit the current confirmation behavior; generic transactional errors otherwise hide which row or version caused the failure.

**How to apply:** Keep analysis write-free, validate the edited rows again in the confirmation endpoint, surface row-level issues before the transaction, and derive the script cache version from the asset's current modification time.