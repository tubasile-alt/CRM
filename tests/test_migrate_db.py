from unittest.mock import Mock, patch

import migrate_db


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