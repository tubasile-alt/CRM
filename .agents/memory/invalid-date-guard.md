---
name: Invalid database dates
description: Legacy PostgreSQL dates outside Python's supported year range can break API serialization and page rendering.
---

Date fields received from forms must be parsed and validated at the API boundary, and legacy date values must be serialized defensively so one corrupt record cannot break an entire agenda response.

**Why:** PostgreSQL can contain dates with years beyond Python's supported range; calling `isoformat()` or calculating age on those values raises an exception during normal page rendering.

**How to apply:** Use strict ISO parsing for new birth-date input and safe serialization/age guards for existing patient data. Treat cleanup of known corrupt production rows as an explicit, separately approved data task.