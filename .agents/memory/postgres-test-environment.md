---
name: PostgreSQL test environment isolation
description: Shell assignment ordering can silently send a disposable migration test to the inherited development database.
---

Always export the temporary `DATABASE_URL` in a separate command or use `env DATABASE_URL=... command`; do not write `DATABASE_URL="new" env ... DATABASE_URL="$DATABASE_URL"`, because the second expansion uses the old shell value.

**Why:** A migration bootstrap test intended for a temporary PostgreSQL cluster ran against the inherited development database when the assignment was expanded before execution. The application log identified the mistake as `PREVIEW/DEV`.

**How to apply:** Before any schema test, print only the non-secret database identity from inside the child process and verify it is the temporary database. Never infer that an inline assignment took effect from the parent shell.