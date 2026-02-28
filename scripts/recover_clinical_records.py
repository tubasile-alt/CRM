import os
import sys
import json
from datetime import datetime, timedelta
from sqlalchemy import text

# Adicionar o diretório raiz ao path para importar o app e models
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from models import db, Appointment, Note, Evolution

# CONFIGURAÇÃO
DRY_RUN = False  # Mude para False para efetivar as mudanças
MAX_HOURS_DIFF = 48

def recover():
    with app.app_context():
        print(f"--- INICIANDO RECUPERAÇÃO DE REGISTROS CLÍNICOS (DRY_RUN={DRY_RUN}) ---")
        
        # 1. Recuperar Notes órfãos
        orphan_notes = Note.query.filter(
            (Note.appointment_id == None) | 
            (~Note.appointment_id.in_(db.session.query(Appointment.id)))
        ).all()
        
        print(f"Encontradas {len(orphan_notes)} notas órfãs.")
        
        notes_relinked = 0
        notes_failed = 0
        
        for note in orphan_notes:
            # Buscar consulta mais próxima
            # Critérios: mesmo paciente, mesma data aproximada (created_at da nota vs start_time da consulta)
            
            # Precisamos de uma consulta que aconteceu perto do momento em que a nota foi criada
            best_match = Appointment.query.filter(
                Appointment.patient_id == note.patient_id
            ).order_by(
                db.func.abs(db.func.extract('epoch', Appointment.start_time) - db.func.extract('epoch', note.created_at))
            ).first()
            
            if best_match:
                diff = abs(best_match.start_time - note.created_at)
                if diff <= timedelta(hours=MAX_HOURS_DIFF):
                    if not DRY_RUN:
                        note.appointment_id = best_match.id
                    notes_relinked += 1
                    # print(f"  [NOTA] Relinked note {note.id} to appt {best_match.id} (diff: {diff})")
                else:
                    notes_failed += 1
                    # print(f"  [NOTA] No close match for note {note.id}. Closest appt {best_match.id} diff is {diff}")
            else:
                notes_failed += 1
                # print(f"  [NOTA] No appointment found for patient {note.patient_id} (note {note.id})")

        # 2. Recuperar Evoluções órfãs
        orphan_evos = Evolution.query.filter(
            (Evolution.consultation_id == None) | 
            (~Evolution.consultation_id.in_(db.session.query(Appointment.id)))
        ).all()
        
        print(f"Encontradas {len(orphan_evos)} evoluções órfãs.")
        
        evos_relinked = 0
        evos_failed = 0
        
        for evo in orphan_evos:
            best_match = Appointment.query.filter(
                Appointment.patient_id == evo.patient_id
            ).order_by(
                db.func.abs(db.func.extract('epoch', Appointment.start_time) - db.func.extract('epoch', evo.evolution_date))
            ).first()
            
            if best_match:
                diff = abs(best_match.start_time - evo.evolution_date)
                if diff <= timedelta(hours=MAX_HOURS_DIFF):
                    if not DRY_RUN:
                        evo.consultation_id = best_match.id
                    evos_relinked += 1
                else:
                    evos_failed += 1
            else:
                evos_failed += 1

        if not DRY_RUN:
            db.session.commit()
            print("Mudanças commitadas no banco de dados.")
            
            # 3. Recalcular sequences (PostgreSQL)
            try:
                print("Recalculando sequences do PostgreSQL...")
                db.session.execute(text("SELECT setval(pg_get_serial_sequence('appointment', 'id'), COALESCE(MAX(id), 1)) FROM appointment;"))
                db.session.execute(text("SELECT setval(pg_get_serial_sequence('note', 'id'), COALESCE(MAX(id), 1)) FROM note;"))
                db.session.execute(text("SELECT setval(pg_get_serial_sequence('evolution', 'id'), COALESCE(MAX(id), 1)) FROM evolution;"))
                db.session.commit()
                print("Sequences recalculadas com sucesso.")
            except Exception as e:
                print(f"Erro ao recalcular sequences (pode ser esperado se não for Postgres): {e}")
        else:
            print("MODO DRY RUN: Nenhuma mudança foi salva.")

        print("\n--- RESUMO DA RECUPERAÇÃO ---")
        print(f"Notas relincadas: {notes_relinked}")
        print(f"Notas sem associação: {notes_failed}")
        print(f"Evoluções relincadas: {evos_relinked}")
        print(f"Evoluções sem associação: {evos_failed}")
        print("------------------------------")

if __name__ == "__main__":
    recover()
