"""
Migração: Adiciona campo appointment_type ao modelo Appointment
Data: 2025-11-11
Descrição: Campo para classificar tipo de consulta (Unimed, Particular, Cortesia)
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from sqlalchemy import text

def migrate():
    """Adiciona coluna appointment_type se não existir"""
    with app.app_context():
        try:
            # Verificar se a coluna já existe
            result = db.session.execute(text("""
                SELECT COUNT(*) 
                FROM pragma_table_info('appointment') 
                WHERE name='appointment_type'
            """))
            exists = result.scalar() > 0
            
            if exists:
                print("✅ Coluna 'appointment_type' já existe")
                return True
            
            # Adicionar coluna
            print("📝 Adicionando coluna 'appointment_type'...")
            db.session.execute(text("""
                ALTER TABLE appointment 
                ADD COLUMN appointment_type VARCHAR(20) DEFAULT 'Particular'
            """))
            db.session.commit()
            
            print("✅ Coluna 'appointment_type' adicionada com sucesso!")
            return True
            
        except Exception as e:
            print(f"❌ Erro na migração: {e}")
            db.session.rollback()
            return False

if __name__ == '__main__':
    print("=== Migração: add_appointment_type ===")
    migrate()
