"""
Migração: Adicionar campo patient_type à tabela patient

Execução: python migrations/add_patient_type.py
"""

import sqlite3
import os

def migrate():
    db_path = os.path.join('instance', 'medcrm.db')
    
    if not os.path.exists(db_path):
        print(f"Erro: Banco de dados não encontrado em {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Verificar se a coluna já existe
        cursor.execute("PRAGMA table_info(patient)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'patient_type' in columns:
            print("✓ Campo 'patient_type' já existe na tabela 'patient'")
        else:
            # Adicionar coluna patient_type
            print("Adicionando campo 'patient_type' à tabela 'patient'...")
            cursor.execute("""
                ALTER TABLE patient 
                ADD COLUMN patient_type VARCHAR(50) DEFAULT 'particular'
            """)
            
            # Atualizar pacientes existentes com valor padrão
            cursor.execute("""
                UPDATE patient 
                SET patient_type = 'particular' 
                WHERE patient_type IS NULL
            """)
            
            conn.commit()
            print("✓ Campo 'patient_type' adicionado com sucesso!")
            print("✓ Pacientes existentes configurados como 'particular'")
        
        # Mostrar estatísticas
        cursor.execute("SELECT COUNT(*) FROM patient")
        total = cursor.fetchone()[0]
        print(f"\nTotal de pacientes no sistema: {total}")
        
    except sqlite3.Error as e:
        print(f"Erro durante migração: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    print("=" * 60)
    print("Migração: Adicionar campo 'patient_type' à tabela 'patient'")
    print("=" * 60)
    migrate()
    print("=" * 60)
