"""Compatibilidade de schema para a auditoria da importação física."""
import threading

from models import PhysicalAgendaImportLog, db


_schema_lock = threading.Lock()
_schema_ready = False


def ensure_physical_agenda_import_schema():
    """Cria a tabela técnica quando o deploy ainda não executou a migration."""
    global _schema_ready
    if _schema_ready:
        return

    with _schema_lock:
        if _schema_ready:
            return
        PhysicalAgendaImportLog.__table__.create(bind=db.engine, checkfirst=True)
        _schema_ready = True
