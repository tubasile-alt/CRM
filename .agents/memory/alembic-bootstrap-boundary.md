---
name: Alembic bootstrap boundary
description: The rule separating new-database model bootstrap from migrations for existing databases.
---

A database without `alembic_version` is bootstrapped from the current SQLAlchemy models and then stamped at the Alembic head. A database with `alembic_version` must be advanced only with `alembic upgrade head`; do not call `create_all()` on that path.

**Why:** Mixing model creation with Alembic leaves tables outside migration history and makes later upgrades attempt to recreate objects that already exist.

**How to apply:** Keep this decision in the migration/post-merge path. Add schema changes as Alembic revisions, and treat legacy databases without a version table as an explicit adoption case rather than allowing versioned runs to fall back to model creation.