"""
Migração: Adicionar campo feminine_hair_transplant à tabela hair_transplant

Execução: python migrations/add_feminine_hair_transplant.py
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
        cursor.execute("PRAGMA table_info(hair_transplant)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'feminine_hair_transplant' in columns:
            print("✓ Campo 'feminine_hair_transplant' já existe na tabela 'hair_transplant'")
        else:
            # Adicionar coluna feminine_hair_transplant
            print("Adicionando campo 'feminine_hair_transplant' à tabela 'hair_transplant'...")
            cursor.execute("""
                ALTER TABLE hair_transplant 
                ADD COLUMN feminine_hair_transplant BOOLEAN DEFAULT 0
            """)
            
            conn.commit()
            print("✓ Campo 'feminine_hair_transplant' adicionado com sucesso!")
        
        # Mostrar estatísticas
        cursor.execute("SELECT COUNT(*) FROM hair_transplant")
        total = cursor.fetchone()[0]
        print(f"\nTotal de planejamentos de transplante capilar: {total}")
        
    except sqlite3.Error as e:
        print(f"Erro durante migração: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    print("=" * 60)
    print("Migração: Adicionar 'feminine_hair_transplant'")
    print("=" * 60)
    migrate()
    print("=" * 60)
