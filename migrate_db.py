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
            
            # Adicionar salas cirúrgicas padrão
            if OperatingRoom.query.count() == 0:
                rooms = [
                    OperatingRoom(name='Sala 1', capacity=1),
                    OperatingRoom(name='Sala 2', capacity=1),
                    OperatingRoom(name='Sala 3', capacity=1)
                ]
                for room in rooms:
                    db.session.add(room)
                print('✓ Salas cirúrgicas criadas')
            
            # Adicionar cores padrão para médicos
            doctors = User.query.filter_by(role='medico').all()
            colors = ['#0d6efd', '#198754', '#dc3545', '#ffc107', '#6f42c1', '#20c997']
            
            for i, doctor in enumerate(doctors):
                if not hasattr(doctor, 'preference') or doctor.preference is None:
                    pref = DoctorPreference(
                        user_id=doctor.id,
                        color=colors[i % len(colors)],
                        layer_enabled=True
                    )
                    db.session.add(pref)
            
            print('✓ Preferências de médicos configuradas')
            
            db.session.commit()
            print('✓ Migração concluída com sucesso!')
            print(f'✓ Backup mantido em: {backup_file}')
            
        except Exception as e:
            db.session.rollback()
            print(f'✗ Erro na migração: {str(e)}')
            print(f'✓ Dados seguros no backup: {backup_file}')
            raise

if __name__ == '__main__':
    migrate_database()
