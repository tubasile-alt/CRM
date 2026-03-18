import argparse
import os
import sys
from datetime import datetime

from sqlalchemy.exc import SQLAlchemyError

CURRENT_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app import app
from config import Config
from models import db, Appointment, Note
from utils.database_backup import backup_manager


PROCEDURE_PLACEHOLDER = '[Conduta registrada via procedimentos]'


def _resolve_sqlite_path(uri: str):
    if not uri or not uri.startswith('sqlite:///'):
        return None
    relative_path = uri.replace('sqlite:///', '', 1)
    return os.path.join(app.root_path, relative_path)


def create_database_backup():
    database_url = os.environ.get('DATABASE_URL') or ''
    if database_url:
        return backup_manager.backup_postgresql(database_url)

    sqlite_path = _resolve_sqlite_path(Config.SQLALCHEMY_DATABASE_URI)
    if sqlite_path and os.path.exists(sqlite_path):
        return backup_manager.backup_sqlite(sqlite_path)

    return None


def should_finalize_note(note: Note) -> bool:
    if note.is_finalized or note.finalized_at:
        return True
    if note.note_type != 'conduta':
        return False
    if note.consultation_duration is not None:
        return True
    if (note.content or '').strip() == PROCEDURE_PLACEHOLDER:
        return True
    if note.indications or note.cosmetic_plans or note.hair_transplants:
        return True
    return False


def run_backfill(apply_changes: bool = False, skip_backup: bool = False):
    with app.app_context():
        backup_path = None
        if not skip_backup:
            backup_path = create_database_backup()

        try:
            notes = Note.query.options(
                db.joinedload(Note.indications),
                db.joinedload(Note.cosmetic_plans),
                db.joinedload(Note.hair_transplants),
                db.joinedload(Note.appointment),
            ).all()
        except SQLAlchemyError as exc:
            return {
                'backup_path': backup_path,
                'notes_to_finalize': 0,
                'appointments_to_finalize': 0,
                'applied': False,
                'error': str(exc),
            }

        notes_to_finalize = []
        appointments_to_finalize = {}

        for note in notes:
            if not should_finalize_note(note):
                continue
            notes_to_finalize.append(note)

            if note.appointment_id:
                finalized_at = note.finalized_at or note.created_at or datetime.utcnow()
                current = appointments_to_finalize.get(note.appointment_id)
                if current is None or finalized_at > current:
                    appointments_to_finalize[note.appointment_id] = finalized_at

        attended_appointments = Appointment.query.filter_by(status='atendido').all()
        for appointment in attended_appointments:
            if appointment.id not in appointments_to_finalize:
                appointments_to_finalize[appointment.id] = appointment.finalized_at or appointment.consultation_date or appointment.start_time

        if apply_changes:
            for note in notes_to_finalize:
                note.is_finalized = True
                note.finalized_at = note.finalized_at or note.created_at
                db.session.add(note)

            for appointment_id, finalized_at in appointments_to_finalize.items():
                appointment = db.session.get(Appointment, appointment_id)
                if not appointment:
                    continue
                appointment.is_finalized = True
                appointment.finalized_at = appointment.finalized_at or finalized_at
                db.session.add(appointment)

            db.session.commit()

        return {
            'backup_path': backup_path,
            'notes_to_finalize': len(notes_to_finalize),
            'appointments_to_finalize': len(appointments_to_finalize),
            'applied': apply_changes,
        }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Backfill de finalização de consultas com backup prévio.')
    parser.add_argument('--apply', action='store_true', help='Aplica as alterações. Sem esta flag, roda em dry-run.')
    parser.add_argument('--skip-backup', action='store_true', help='Pula a criação de backup antes do backfill.')
    args = parser.parse_args()

    result = run_backfill(apply_changes=args.apply, skip_backup=args.skip_backup)
    print('Resultado do backfill:')
    print(result)
