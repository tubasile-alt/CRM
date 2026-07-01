import os
import shutil
from datetime import datetime
from app import app, db
from models import OperatingRoom, Surgery, DoctorPreference, User
from services.push_schema_service import ensure_push_subscription_schema

def backup_database():
    """Cria backup do banco de dados antes da migração"""
    if os.path.exists('medcrm.db'):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f'medcrm_backup_{timestamp}.db'
        shutil.copy2('medcrm.db', backup_name)
        print(f'✓ Backup criado: {backup_name}')
        return backup_name
    return None

def create_partial_unique_index():
    """
    Cria o índice único parcial no PostgreSQL para garantir unicidade de
    patient_code na faixa nova (>= 1001) sem afetar códigos históricos.
    """
    with app.app_context():
        if not db.engine.dialect.name == 'postgresql':
            print('  (SQLite detectado; índice parcial não necessário)')
            return

        # Criar o índice parcial se ainda não existir
        db.session.execute(
            db.text("""
                CREATE UNIQUE INDEX IF NOT EXISTS idx_unique_new_code
                ON patient_doctor (doctor_id, patient_code)
                WHERE patient_code >= 1001;
            """)
        )
        db.session.commit()
        print('✓ Índice único parcial (patient_code >= 1001) criado/verificado')

def migrate_database():
    """Migra o banco de dados adicionando novas tabelas e colunas"""
    with app.app_context():
        print('Iniciando migração segura do banco de dados...')
        
        # Criar backup primeiro
        backup_file = backup_database()
        
        try:
            # Criar novas tabelas (se não existirem)
            db.create_all()
            print('✓ Novas tabelas criadas com sucesso')

            ensure_push_subscription_schema()
            print('✓ Estrutura de notificações push criada/verificada')
            
            # Criar índice único parcial (FASE 1)
            print('  Verificando índice único parcial para patient_doctor...')
            create_partial_unique_index()
            
            db.session.commit()
            print('✓ Migração concluída com sucesso!')
            if backup_file:
                print(f'✓ Backup mantido em: {backup_file}')
            
        except Exception as e:
            db.session.rollback()
            print(f'✗ Erro na migração: {str(e)}')
            if backup_file:
                print(f'✓ Dados seguros no backup: {backup_file}')
            raise

if __name__ == '__main__':
    migrate_database()
