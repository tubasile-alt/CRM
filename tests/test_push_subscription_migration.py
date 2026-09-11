import importlib.util
from pathlib import Path

from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy import create_engine, inspect


MIGRATION_PATH = (
    Path(__file__).parents[1]
    / 'migrations'
    / 'versions'
    / 'c9d8e7f6a5b4_add_push_subscription_diagnostics.py'
)


def _load_migration():
    spec = importlib.util.spec_from_file_location(
        'push_subscription_diagnostics_migration',
        MIGRATION_PATH,
    )
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)
    return migration


def _upgrade(connection):
    migration = _load_migration()
    context = MigrationContext.configure(connection)
    with Operations.context(context):
        migration.upgrade()


def _create_push_subscription_table(connection, extra_columns=''):
    connection.exec_driver_sql(
        f"""
        CREATE TABLE push_subscription (
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            endpoint TEXT NOT NULL
            {extra_columns}
        )
        """
    )


def test_diagnostics_migration_adds_missing_columns():
    engine = create_engine('sqlite:///:memory:')

    with engine.begin() as connection:
        _create_push_subscription_table(connection)

        _upgrade(connection)

        columns = {
            column['name']
            for column in inspect(connection).get_columns('push_subscription')
        }

    assert {
        'endpoint_partial',
        'platform',
        'last_test_at',
        'last_error',
    }.issubset(columns)


def test_diagnostics_migration_adopts_columns_from_legacy_schema():
    engine = create_engine('sqlite:///:memory:')

    with engine.begin() as connection:
        _create_push_subscription_table(
            connection,
            """
            ,
            endpoint_partial VARCHAR(255),
            platform VARCHAR(50),
            last_test_at DATETIME,
            last_error TEXT
            """,
        )

        _upgrade(connection)

        columns = [
            column['name']
            for column in inspect(connection).get_columns('push_subscription')
        ]

    assert columns == [
        'id',
        'user_id',
        'endpoint',
        'endpoint_partial',
        'platform',
        'last_test_at',
        'last_error',
    ]