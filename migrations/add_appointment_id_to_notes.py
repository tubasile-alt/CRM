"""
Migração: Adicionar appointment_id à tabela Note para agrupamento de consultas

Este script adiciona o campo appointment_id (FK opcional) ao modelo Note
para permitir agrupamento determinístico de notas da mesma consulta.

Estratégia:
- Adiciona coluna appointment_id como nullable (compatibilidade com dados antigos)
- Cria índice composto para performance
- Notas antigas permanecem com appointment_id = NULL (usam fallback temporal)
- Novas notas terão appointment_id preenchido automaticamente
"""

import sqlite3
from datetime import datetime

def run_migration(db_path='instance/medcrm.db'):
    print(f"[{datetime.now()}] Iniciando migração: add_appointment_id_to_notes")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Verificar se a coluna já existe
        cursor.execute("PRAGMA table_info(note)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'appointment_id' in columns:
            print("⚠️  Coluna 'appointment_id' já existe. Migração já foi executada.")
            conn.close()
            return
        
        print("✓ Adicionando coluna 'appointment_id' à tabela 'note'...")
        cursor.execute("""
            ALTER TABLE note 
            ADD COLUMN appointment_id INTEGER 
            REFERENCES appointment(id)
        """)
        
        print("✓ Criando índice composto para performance...")
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_note_patient_appt_type 
            ON note(patient_id, appointment_id, note_type)
        """)
        
        # Commit das mudanças
        conn.commit()
        
        # Verificar quantas notas existem
        cursor.execute("SELECT COUNT(*) FROM note")
        total_notes = cursor.fetchone()[0]
        
        print(f"✓ Migração concluída com sucesso!")
        print(f"  - Total de notas no banco: {total_notes}")
        print(f"  - Notas antigas mantidas com appointment_id = NULL (usarão fallback temporal)")
        print(f"  - Novas notas terão appointment_id preenchido automaticamente")
        
    except Exception as e:
        print(f"✗ Erro durante migração: {e}")
        conn.rollback()
        raise
    
    finally:
        conn.close()
        print(f"[{datetime.now()}] Migração finalizada\n")

if __name__ == '__main__':
    run_migration()
