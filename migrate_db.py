import os
import shutil
from datetime import datetime
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import inspect

from app import app, db


MIGRATIONS_DIR = Path(__file__).resolve().parent / 'migrations'

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

def ensure_medication_columns():
    """Garante que as colunas de etiquetagem existam na tabela medications."""
    with app.app_context():
        if not db.engine.dialect.name == 'postgresql':
            return
        cols = db.session.execute(db.text(
            "SELECT column_name FROM information_schema.columns WHERE table_name = 'medications'"
        )).fetchall()
        col_names = {c[0] for c in cols}
        if 'categoria' not in col_names:
            db.session.execute(db.text("ALTER TABLE medications ADD COLUMN categoria VARCHAR(100)"))
            print('  + Coluna categoria adicionada')
        if 'indicacoes' not in col_names:
            db.session.execute(db.text("ALTER TABLE medications ADD COLUMN indicacoes JSONB"))
            print('  + Coluna indicacoes adicionada')
        if 'etiqueta_revisada' not in col_names:
            db.session.execute(db.text("ALTER TABLE medications ADD COLUMN etiqueta_revisada BOOLEAN DEFAULT FALSE"))
            print('  + Coluna etiqueta_revisada adicionada')
        db.session.commit()


def ensure_patient_marketing_column():
    """Garante que a preferência de marketing exista na tabela patient."""
    with app.app_context():
        if db.engine.dialect.name != 'postgresql':
            return
        cols = db.session.execute(db.text(
            "SELECT column_name FROM information_schema.columns WHERE table_name = 'patient'"
        )).fetchall()
        col_names = {c[0] for c in cols}
        if 'accepts_marketing' not in col_names:
            db.session.execute(db.text(
                "ALTER TABLE patient "
                "ADD COLUMN accepts_marketing BOOLEAN DEFAULT TRUE NOT NULL"
            ))
            print('  + Coluna accepts_marketing adicionada')
        db.session.commit()


def _alembic_config():
    """Retorna uma configuração Alembic ligada ao diretório deste projeto."""
    config = Config(str(MIGRATIONS_DIR / 'alembic.ini'))
    config.set_main_option('script_location', str(MIGRATIONS_DIR))
    return config


def has_alembic_version_table():
    """Indica se o banco já participa do histórico de migrations."""
    return inspect(db.engine).has_table('alembic_version')


def bootstrap_new_database():
    """Cria um banco novo a partir dos modelos e o carimba no head."""
    db.create_all()
    print('✓ Schema inicial criado a partir dos modelos')
    command.stamp(_alembic_config(), 'head')
    print('✓ Banco novo carimbado no head do Alembic')


def upgrade_versioned_database():
    """Aplica somente as migrations pendentes em um banco versionado."""
    command.upgrade(_alembic_config(), 'head')
    print('✓ Migrations Alembic aplicadas até o head')


def migrate_database():
    """Sincroniza o banco sem misturar bootstrap de modelos e Alembic."""
    with app.app_context():
        print('Iniciando migração segura do banco de dados...')

        # Criar backup primeiro
        backup_file = backup_database()

        try:
            if has_alembic_version_table():
                print('✓ alembic_version encontrado; executando upgrade head')
                upgrade_versioned_database()
            else:
                print('✓ alembic_version ausente; inicializando banco novo')
                bootstrap_new_database()

            # Estas correções mantêm compatibilidade com bases legadas que
            # antecedem as migrations correspondentes. Não criam tabelas.
            ensure_medication_columns()
            ensure_patient_marketing_column()
            
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
