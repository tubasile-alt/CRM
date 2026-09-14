---
name: SQLite test isolation
description: Mixed Flask-SQLAlchemy tests can reuse an in-memory SQLite session across independently configured Flask apps.
---

Some test modules create new Flask apps with `sqlite:///:memory:` while other tests use the global application fixture. When those suites run together, the scoped SQLAlchemy session can retain the previous app's in-memory database and produce duplicate-key failures; the affected module may still pass alone.

**Why:** The SQLAlchemy extension and scoped session are process-global, while the test apps assume each `db.init_app(app)` creates a fully isolated session for the next test.

**How to apply:** Treat isolated module runs as the reliable signal for these legacy tests, and fix the fixture/session lifecycle before using a full-suite failure as evidence of a feature regression.