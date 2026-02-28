import os
import sys
from datetime import datetime

# Adicionar o diretório raiz ao path para importar o app e models
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from models import db, Appointment, Note, Evolution

def generate():
    with app.app_context():
        print("--- INICIANDO GERAÇÃO DE EVOLUÇÕES FALTANTES ---")
        
        appointments = Appointment.query.all()
        print(f"Analisando {len(appointments)} consultas...")
        
        evolutions_created = 0
        
        for appt in appointments:
            # Verificar se já existe evolução para esta consulta
            existing_evo = Evolution.query.filter_by(consultation_id=appt.id).first()
            if existing_evo:
                continue
            
            # Buscar notas associadas a esta consulta
            notes = Note.query.filter_by(appointment_id=appt.id).all()
            if not notes:
                continue
            
            # Organizar notas por tipo para concatenar na ordem correta
            notes_by_type = {n.note_type: n.content for n in notes}
            
            content_parts = []
            
            # Seguir a ordem lógica do prontuário
            if 'queixa' in notes_by_type:
                content_parts.append(f"Queixa principal: {notes_by_type['queixa']}")
            if 'anamnese' in notes_by_type:
                content_parts.append(f"Exame/Anamnese: {notes_by_type['anamnese']}")
            if 'diagnostico' in notes_by_type:
                content_parts.append(f"Diagnóstico: {notes_by_type['diagnostico']}")
            if 'conduta' in notes_by_type:
                content_parts.append(f"Conduta: {notes_by_type['conduta']}")
            
            if not content_parts:
                # Se não houver tipos padrão, tenta pegar qualquer conteúdo disponível
                all_content = "\n".join([n.content for n in notes if n.content])
                if all_content:
                    content_parts.append(all_content)
            
            if content_parts:
                evolution_content = "\n\n".join(content_parts)
                
                if not evolution_content.strip():
                    continue

                # Criar ou atualizar a evolução
                if existing_evo:
                    if not existing_evo.content or not existing_evo.content.strip():
                        existing_evo.content = evolution_content
                        evolutions_created += 1
                    continue
                
                # Usar o doctor_id da primeira nota ou da consulta
                doctor_id = notes[0].doctor_id if notes else appt.doctor_id
                
                new_evo = Evolution(
                    patient_id=appt.patient_id,
                    doctor_id=doctor_id,
                    consultation_id=appt.id,
                    evolution_date=appt.start_time,
                    content=evolution_content
                )
                db.session.add(new_evo)
                evolutions_created += 1

        db.session.commit()
        print(f"\n--- RESUMO ---")
        print(f"Consultas analisadas: {len(appointments)}")
        print(f"Evoluções criadas: {evolutions_created}")
        print("------------------------------")

if __name__ == "__main__":
    generate()
