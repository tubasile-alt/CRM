import importlib.util
from pathlib import Path

import pytest
from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy import create_engine, inspect


MIGRATION_PATH = (
    Path(__file__).parents[1]
    / 'migrations'
    / 'versions'
    / 'd1e2f3a4b5c6_create_patient_photo_table.py'
)


def _load_migration():
    spec = importlib.util.spec_from_file_location(
        'patient_photo_migration',
        MIGRATION_PATH,
    )
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)
    return migration


def _upgrade(connection):
    context = MigrationContext.configure(connection)
    with Operations.context(context):
        _load_migration().upgrade()


def _create_patient_photo_table(connection, columns):
    connection.exec_driver_sql(
        f"""
        CREATE TABLE patient_photo (
            {columns}
        )
        """
    )


def test_patient_photo_migration_adopts_valid_legacy_table():
    engine = create_engine('sqlite:///:memory:')

    with engine.begin() as connection:
        _create_patient_photo_table(
            connection,
            """
            id INTEGER PRIMARY KEY,
            patient_id INTEGER NOT NULL,
            data BLOB NOT NULL,
            mime_type VARCHAR(50) NOT NULL,
            updated_at DATETIME NOT NULL
            """,
        )
        connection.exec_driver_sql(
            'CREATE UNIQUE INDEX idx_patient_photo_patient_id '
            'ON patient_photo (patient_id)'
        )

        _upgrade(connection)

        assert inspect(connection).has_table('patient_photo')


def test_patient_photo_migration_rejects_incomplete_legacy_table():
    engine = create_engine('sqlite:///:memory:')

    with engine.begin() as connection:
        _create_patient_photo_table(
            connection,
            """
            id INTEGER PRIMARY KEY,
            patient_id INTEGER NOT NULL
            """,
        )

        with pytest.raises(RuntimeError, match='está incompleta'):
            _upgrade(connection)