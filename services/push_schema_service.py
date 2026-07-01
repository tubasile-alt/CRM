"""Compatibilidade de schema para o armazenamento de Web Push."""
import threading

from sqlalchemy import inspect

from models import PushSubscription, db


_schema_lock = threading.Lock()
_schema_ready = False

_DIAGNOSTIC_COLUMNS = {
    'endpoint_partial': 'VARCHAR(140)',
    'platform': 'VARCHAR(40)',
    'last_test_at': 'TIMESTAMP',
    'last_error': 'TEXT',
}


def ensure_push_subscription_schema():
    """Cria a tabela e completa colunas legadas sem depender do deploy runner."""
    global _schema_ready
    if _schema_ready:
        return

    with _schema_lock:
        if _schema_ready:
            return

        PushSubscription.__table__.create(bind=db.engine, checkfirst=True)
        existing_columns = {
            column['name']
            for column in inspect(db.engine).get_columns(PushSubscription.__tablename__)
        }
        missing_columns = {
            name: sql_type
            for name, sql_type in _DIAGNOSTIC_COLUMNS.items()
            if name not in existing_columns
        }

        if missing_columns:
            dialect = db.engine.dialect.name
            with db.engine.begin() as connection:
                for name, sql_type in missing_columns.items():
                    if dialect == 'postgresql':
                        statement = (
                            f'ALTER TABLE push_subscription '
                            f'ADD COLUMN IF NOT EXISTS {name} {sql_type}'
                        )
                    else:
                        statement = (
                            f'ALTER TABLE push_subscription '
                            f'ADD COLUMN {name} {sql_type}'
                        )
                    connection.execute(db.text(statement))

        _schema_ready = True
