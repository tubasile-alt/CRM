---
name: Alembic bootstrap boundary
description: The rule separating new-database model bootstrap from migrations for existing databases.
---

A database without `alembic_version` is bootstrapped from the current SQLAlchemy models and then stamped at the Alembic head. A database with `alembic_version` must be advanced only with `alembic upgrade head`; do not call `create_all()` on that path. Versioned legacy databases can still contain objects created by an older runtime helper, so create/column migrations must adopt existing objects only after validating the required shape and must fail explicitly when the shape is incomplete.

**Why:** Mixing model creation with Alembic leaves tables outside migration history and makes later upgrades attempt to recreate objects that already exist. A Preview database demonstrated that `alembic_version` can lag behind tables and columns created by the old compatibility helper.

**How to apply:** Keep this decision in the migration/post-merge path. Add schema changes as Alembic revisions, inspect existing legacy objects before adopting them, and treat legacy databases without a version table as an explicit adoption case rather than allowing versioned runs to fall back to model creation or stamping solely because a table exists.