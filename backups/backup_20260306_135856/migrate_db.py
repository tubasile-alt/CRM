import os
import shutil
from datetime import datetime
from app import app, db
from models import OperatingRoom, Surgery, DoctorPreference, User

def backup_database():
    """Cria backup do banco de dados antes da migração"""
    if os.path.exists('medcrm.db'):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f'medcrm_backup_{timestamp}.db'
        shutil.copy2('medcrm.db', backup_name)
        print(f'✓ Backup criado: {backup_name}')
        return backup_name
    return None

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
