#!/bin/bash
set -e

cd "$(dirname "$0")/.."
pip install -r requirements.txt -q
# migrate_db.py chooses bootstrap for a new database and Alembic upgrade for
# databases that already have an alembic_version table.
python migrate_db.py
