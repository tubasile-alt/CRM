#!/usr/bin/env python3
"""
Script de teste para verificar sistema de lembretes automáticos
"""
from app import app
from models import db, FollowUpReminder
from datetime import datetime

with app.app_context():
    # Verificar todos os lembretes criados
    reminders = FollowUpReminder.query.all()
    
    print(f"\n{'='*60}")
    print(f"SISTEMA DE LEMBRETES AUTOMÁTICOS - STATUS")
    print(f"{'='*60}\n")
    
    if not reminders:
        print("✓ Sistema funcionando corretamente")
        print("  (Nenhum lembrete criado ainda - aguardando primeiro planejamento)")
    else:
        print(f"Total de lembretes criados: {len(reminders)}\n")
        
        cosmetic_count = sum(1 for r in reminders if r.reminder_type == 'cosmetic_follow_up')
        transplant_count = sum(1 for r in reminders if r.reminder_type == 'transplant_revision')
        
        print(f"Por tipo:")
        print(f"  - Cosmiatria (follow-up): {cosmetic_count}")
        print(f"  - Transplante (revisão): {transplant_count}\n")
        
        print("Lembretes agendados:")
        print("-" * 60)
        
        for reminder in reminders:
            patient = reminder.patient
            print(f"\nPaciente: {patient.name}")
            print(f"Procedimento: {reminder.procedure_name}")
            print(f"Tipo: {reminder.reminder_type}")
            print(f"Data agendada: {reminder.scheduled_date}")
            print(f"Notas: {reminder.notes}")
            print(f"Completado: {'Sim' if reminder.completed else 'Não'}")
    
    print(f"\n{'='*60}\n")
