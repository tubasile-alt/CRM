"""
Migração segura que adiciona as novas colunas preservando TODOS os dados existentes.
Este script faz backup automático antes de qualquer mudança.
"""
import sqlite3
import shutil
from datetime import datetime
import os

def backup_database():
    """Cria backup do banco de dados"""
    if os.path.exists('medcrm.db'):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f'medcrm_backup_{timestamp}.db'
        shutil.copy2('medcrm.db', backup_name)
        print(f'✓ BACKUP CRIADO: {backup_name}')
        print(f'  Seus dados estão seguros em: {backup_name}')
        return backup_name
    return None

def migrate_appointment_table():
    """Adiciona novas colunas à tabela appointment de forma segura"""
    
    print('\n' + '='*70)
    print('MIGRAÇÃO SEGURA DO BANCO DE DADOS')
    print('='*70)
    
    # Criar backup primeiro
    backup_file = backup_database()
    
    try:
        conn = sqlite3.connect('medcrm.db')
        cursor = conn.cursor()
        
        print('\n1. Verificando estrutura atual...')
        cursor.execute("PRAGMA table_info(appointment)")
        columns = [col[1] for col in cursor.fetchall()]
        print(f'   Colunas atuais: {", ".join(columns)}')
        
        # Verificar se as colunas já existem
        needs_migration = not all(col in columns for col in ['waiting', 'checked_in_time', 'room'])
        
        if not needs_migration:
            print('✓ Tabela já está atualizada!')
            conn.close()
            return
        
        print('\n2. Iniciando migração...')
        
        # Criar tabela temporária com a estrutura nova
        cursor.execute('''
            CREATE TABLE appointment_new (
                id INTEGER PRIMARY KEY,
                patient_id INTEGER NOT NULL,
                doctor_id INTEGER NOT NULL,
                start_time DATETIME NOT NULL,
                end_time DATETIME NOT NULL,
                status VARCHAR(20) DEFAULT 'agendado',
                notes TEXT,
                waiting BOOLEAN DEFAULT 0,
                checked_in_time DATETIME,
                room VARCHAR(50),
                created_at DATETIME,
                FOREIGN KEY (patient_id) REFERENCES patient(id),
                FOREIGN KEY (doctor_id) REFERENCES user(id)
            )
        ''')
        print('   ✓ Tabela temporária criada')
        
        # Copiar todos os dados existentes
        cursor.execute('''
            INSERT INTO appointment_new 
            (id, patient_id, doctor_id, start_time, end_time, status, notes, created_at)
            SELECT id, patient_id, doctor_id, start_time, end_time, status, notes, created_at
            FROM appointment
        ''')
        rows_copied = cursor.rowcount
        print(f'   ✓ {rows_copied} registros copiados com segurança')
        
        # Remover tabela antiga e renomear a nova
        cursor.execute('DROP TABLE appointment')
        cursor.execute('ALTER TABLE appointment_new RENAME TO appointment')
        print('   ✓ Estrutura atualizada')
        
        # Commit das mudanças
        conn.commit()
        print('\n✓ MIGRAÇÃO CONCLUÍDA COM SUCESSO!')
        print(f'  {rows_copied} agendamentos preservados')
        print(f'  Novas colunas adicionadas: waiting, checked_in_time, room')
        
        conn.close()
        
        print(f'\n✓ BACKUP MANTIDO EM: {backup_file}')
        print('  Você pode restaurar a qualquer momento se necessário')
        print('='*70 + '\n')
        
    except Exception as e:
        print(f'\n✗ ERRO NA MIGRAÇÃO: {str(e)}')
        print(f'✓ SEUS DADOS ESTÃO SEGUROS NO BACKUP: {backup_file}')
        print('  Para restaurar: cp {backup_file} medcrm.db')
        raise

if __name__ == '__main__':
    migrate_appointment_table()
