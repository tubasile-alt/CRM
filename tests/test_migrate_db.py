from unittest.mock import Mock, patch

import pytest
from alembic.script import ScriptDirectory
from flask import Flask
from sqlalchemy import inspect

import migrate_db
from models import db


def test_new_database_bootstrap_creates_schema_then_stamps_head():
    alembic_config = Mock()
    with patch.object(migrate_db, '_alembic_config', return_value=alembic_config), \
            patch.object(migrate_db.db, 'create_all') as create_all, \
            patch.object(migrate_db.command, 'stamp') as stamp:
        migrate_db.bootstrap_new_database()

    create_all.assert_called_once_with()
    stamp.assert_called_once_with(alembic_config, 'head')


def test_versioned_database_uses_upgrade_without_create_all():
    alembic_config = Mock()
    with patch.object(migrate_db, '_alembic_config', return_value=alembic_config), \
            patch.object(migrate_db.command, 'upgrade') as upgrade, \
            patch.object(migrate_db.db, 'create_all') as create_all:
        migrate_db.upgrade_versioned_database()

    upgrade.assert_called_once_with(alembic_config, 'head')
    create_all.assert_not_called()


def test_migration_path_selects_bootstrap_for_database_without_version_table():
    with patch.object(migrate_db, 'has_alembic_version_table', return_value=False), \
            patch.object(migrate_db, 'bootstrap_new_database') as bootstrap, \
            patch.object(migrate_db, 'upgrade_versioned_database') as upgrade, \
            patch.object(migrate_db, 'backup_database', return_value=None), \
            patch.object(migrate_db, 'ensure_medication_columns'), \
            patch.object(migrate_db, 'ensure_patient_marketing_column'), \
            patch.object(migrate_db, 'create_partial_unique_index'), \
            patch.object(migrate_db.db.session, 'commit'):
        with migrate_db.app.app_context():
            migrate_db.migrate_database()

    bootstrap.assert_called_once_with()
    upgrade.assert_not_called()


def test_migration_path_selects_upgrade_for_versioned_database():
    with patch.object(migrate_db, 'has_alembic_version_table', return_value=True), \
            patch.object(migrate_db, 'bootstrap_new_database') as bootstrap, \
            patch.object(migrate_db, 'upgrade_versioned_database') as upgrade, \
            patch.object(migrate_db, 'backup_database', return_value=None), \
            patch.object(migrate_db, 'ensure_medication_columns'), \
            patch.object(migrate_db, 'ensure_patient_marketing_column'), \
            patch.object(migrate_db, 'create_partial_unique_index'), \
            patch.object(migrate_db.db.session, 'commit'):
        with migrate_db.app.app_context():
            migrate_db.migrate_database()

    upgrade.assert_called_once_with()
    bootstrap.assert_not_called()


@pytest.fixture
def isolated_migration_app(tmp_path, monkeypatch):
    """Use a throwaway SQLite database without touching the app's configured DB."""
    database_path = tmp_path / 'migration-test.sqlite'
    test_app = Flask('isolated-migration-test')
    test_app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI=f'sqlite:///{database_path}',
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )
    db.init_app(test_app)
    monkeypatch.setattr(migrate_db, 'app', test_app)

    with test_app.app_context():
        yield test_app
        db.session.remove()
        db.engine.dispose()


def _migration_head():
    script = ScriptDirectory.from_config(migrate_db._alembic_config())
    return script.get_current_head()


def _database_version():
    return db.session.execute(
        db.text('SELECT version_num FROM alembic_version')
    ).scalar_one()


def test_bootstrap_integration_creates_and_stamps_throwaway_database(
    isolated_migration_app,
):
    with isolated_migration_app.app_context():
        migrate_db.bootstrap_new_database()

        assert inspect(db.engine).has_table('alembic_version')
        assert _database_version() == _migration_head()


def test_versioned_database_integration_upgrades_pending_revision_without_create_all(
    isolated_migration_app,
):
    with isolated_migration_app.app_context():
        migrate_db.bootstrap_new_database()
        head = _migration_head()

        # Build a real, versioned database one revision behind the head.
        migrate_db.command.downgrade(
            migrate_db._alembic_config(),
            'g8b9c0d1e2f3',
        )
        assert _database_version() == 'g8b9c0d1e2f3'
        assert 'attempts' not in {
            column['name']
            for column in inspect(db.engine).get_columns('message_dispatch')
        }

        with patch.object(migrate_db.db, 'create_all') as create_all, \
                patch.object(migrate_db, 'backup_database', return_value=None):
            migrate_db.migrate_database()

        create_all.assert_not_called()
        assert _database_version() == head
        assert 'attempts' in {
            column['name']
            for column in inspect(db.engine).get_columns('message_dispatch')
        }
