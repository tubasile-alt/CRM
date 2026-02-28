import os
import sys
from datetime import datetime

# Adicionar o diretório raiz ao path para importar o app e models
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from models import db, Appointment, Note, Evolution

def regenerate(appointment_id):
    with app.app_context():
        appt = db.session.get(Appointment, int(appointment_id))
        if not appt:
            print(f"Erro: Appointment {appointment_id} não encontrado.")
            return

        print(f"--- REGENERANDO EVOLUÇÃO PARA APPOINTMENT {appointment_id} ---")
        
        # Buscar notas associadas
        notes = Note.query.filter_by(appointment_id=appt.id).all()
        
        content_parts = []
        notes_by_type = {n.note_type: n.content for n in notes}
        
        if 'queixa' in notes_by_type:
            content_parts.append(f"Queixa principal: {notes_by_type['queixa']}")
        if 'anamnese' in notes_by_type:
            content_parts.append(f"Exame/Anamnese: {notes_by_type['anamnese']}")
        if 'diagnostico' in notes_by_type:
            content_parts.append(f"Diagnóstico: {notes_by_type['diagnostico']}")
        if 'conduta' in notes_by_type:
            content_parts.append(f"Conduta: {notes_by_type['conduta']}")
            
        if not content_parts:
            all_content = "\n".join([n.content for n in notes if n.content])
            if all_content:
                content_parts.append(all_content)
        
        if not content_parts:
            print("Nenhum conteúdo clínico encontrado nas notas.")
            return

        evolution_content = "\n\n".join(content_parts)
        
        # Buscar ou criar evolução
        evo = Evolution.query.filter_by(consultation_id=appt.id).first()
        if evo:
            if not evo.content or not evo.content.strip():
                evo.content = evolution_content
                print("Evolução existente estava vazia. Conteúdo atualizado.")
            else:
                print("Evolução já possui conteúdo. Nenhuma alteração feita.")
        else:
            doctor_id = notes[0].doctor_id if notes else appt.doctor_id
            new_evo = Evolution(
                patient_id=appt.patient_id,
                doctor_id=doctor_id,
                consultation_id=appt.id,
                evolution_date=appt.start_time,
                content=evolution_content
            )
            db.session.add(new_evo)
            print("Nova evolução criada.")
            
        db.session.commit()
        print("Operação concluída.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        regenerate(sys.argv[1])
    else:
        # Fallback para o caso 288 (Appointment 331)
        regenerate(331)
