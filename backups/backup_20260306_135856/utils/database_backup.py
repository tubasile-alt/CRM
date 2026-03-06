"""
Sistema de Backup e Recuperação de Dados
Garante que os dados não sejam perdidos em nenhuma atualização
"""

import os
import gzip
import json
import sqlite3
import psycopg2
from datetime import datetime
from pathlib import Path
import subprocess


class DatabaseBackupManager:
    """Gerencia backups do banco de dados SQLite e PostgreSQL"""
    
    def __init__(self, backup_dir='backups'):
        self.backup_dir = backup_dir
        self.max_backups = 50  # Manter últimos 50 backups
        Path(backup_dir).mkdir(exist_ok=True)
        
    def backup_sqlite(self, db_path='instance/medcrm.db', compress=True):
        """
        Cria backup do banco SQLite
        
        Args:
            db_path: Caminho do banco SQLite
            compress: Se deve comprimir com gzip
            
        Returns:
            str: Caminho do arquivo de backup
        """
        if not os.path.exists(db_path):
            raise FileNotFoundError(f"Banco SQLite não encontrado: {db_path}")
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        dump_file = os.path.join(self.backup_dir, f'sqlite_dump_{timestamp}.sql')
        
        # Exportar SQLite para SQL
        try:
            conn = sqlite3.connect(db_path)
            with open(dump_file, 'w') as f:
                for line in conn.iterdump():
                    f.write(f'{line}\n')
            conn.close()
            
            # Comprimir
            if compress:
                with open(dump_file, 'rb') as f_in:
                    with gzip.open(f'{dump_file}.gz', 'wb') as f_out:
                        f_out.write(f_in.read())
                os.remove(dump_file)
                backup_path = f'{dump_file}.gz'
            else:
                backup_path = dump_file
            
            # Registrar metadata
            self._log_backup({
                'type': 'sqlite',
                'timestamp': datetime.now().isoformat(),
                'file': os.path.basename(backup_path),
                'size': os.path.getsize(backup_path),
                'compressed': compress
            })
            
            self._cleanup_old_backups('sqlite')
            return backup_path
            
        except Exception as e:
            if os.path.exists(dump_file):
                os.remove(dump_file)
            raise e
    
    def backup_postgresql(self, database_url, compress=True):
        """
        Cria backup do banco PostgreSQL usando pg_dump
        
        Args:
            database_url: URL de conexão PostgreSQL
            compress: Se deve comprimir com gzip
            
        Returns:
            str: Caminho do arquivo de backup
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        dump_file = os.path.join(self.backup_dir, f'postgres_dump_{timestamp}.sql')
        
        try:
            # Usar pg_dump para backup
            cmd = f'pg_dump "{database_url}" > "{dump_file}"'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode != 0:
                raise Exception(f"pg_dump erro: {result.stderr}")
            
            # Comprimir
            if compress:
                with open(dump_file, 'rb') as f_in:
                    with gzip.open(f'{dump_file}.gz', 'wb') as f_out:
                        f_out.write(f_in.read())
                os.remove(dump_file)
                backup_path = f'{dump_file}.gz'
            else:
                backup_path = dump_file
            
            # Registrar metadata
            self._log_backup({
                'type': 'postgresql',
                'timestamp': datetime.now().isoformat(),
                'file': os.path.basename(backup_path),
                'size': os.path.getsize(backup_path),
                'compressed': compress
            })
            
            self._cleanup_old_backups('postgresql')
            return backup_path
            
        except Exception as e:
            if os.path.exists(dump_file):
                os.remove(dump_file)
            raise e
    
    def restore_sqlite(self, backup_file, db_path='instance/medcrm.db'):
        """
        Restaura backup do SQLite
        
        Args:
            backup_file: Arquivo de backup ou caminho
            db_path: Onde restaurar o banco
            
        Returns:
            bool: True se restaurado com sucesso
        """
        if not os.path.isabs(backup_file):
            backup_file = os.path.join(self.backup_dir, backup_file)
        
        if not os.path.exists(backup_file):
            raise FileNotFoundError(f"Backup não encontrado: {backup_file}")
        
        # Criar backup do estado atual antes de restaurar
        print(f"🔄 Criando backup do estado atual antes de restaurar...")
        current_backup = self.backup_sqlite(db_path)
        print(f"✅ Backup atual salvo em: {current_backup}")
        
        # Descomprimir se necessário
        temp_file = backup_file
        if backup_file.endswith('.gz'):
            temp_file = backup_file[:-3]
            with gzip.open(backup_file, 'rb') as f_in:
                with open(temp_file, 'wb') as f_out:
                    f_out.write(f_in.read())
        
        # Restaurar
        try:
            conn = sqlite3.connect(db_path)
            with open(temp_file, 'r') as f:
                sql = f.read()
                conn.executescript(sql)
            conn.close()
            
            print(f"✅ Banco restaurado com sucesso de: {backup_file}")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao restaurar: {e}")
            raise
        
        finally:
            if temp_file != backup_file:
                os.remove(temp_file)
    
    def list_backups(self, backup_type=None):
        """
        Lista backups disponíveis
        
        Args:
            backup_type: 'sqlite', 'postgresql' ou None (ambos)
            
        Returns:
            list: Lista de backups com metadata
        """
        backups = []
        for filename in os.listdir(self.backup_dir):
            if filename.startswith('sqlite_dump_') or filename.startswith('postgres_dump_'):
                filepath = os.path.join(self.backup_dir, filename)
                btype = 'sqlite' if 'sqlite_dump_' in filename else 'postgresql'
                
                if backup_type and btype != backup_type:
                    continue
                
                backups.append({
                    'file': filename,
                    'path': filepath,
                    'type': btype,
                    'size': os.path.getsize(filepath),
                    'size_mb': round(os.path.getsize(filepath) / (1024 * 1024), 2),
                    'modified': datetime.fromtimestamp(os.path.getmtime(filepath))
                })
        
        backups.sort(key=lambda x: x['modified'], reverse=True)
        return backups
    
    def _log_backup(self, backup_info):
        """Registra informações sobre o backup"""
        log_file = os.path.join(self.backup_dir, 'backup_log.json')
        
        logs = []
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                try:
                    logs = json.load(f)
                except:
                    logs = []
        
        logs.append(backup_info)
        
        with open(log_file, 'w') as f:
            json.dump(logs, f, indent=2)
    
    def _cleanup_old_backups(self, backup_type):
        """Remove backups antigos mantendo apenas os mais recentes"""
        prefix = 'sqlite_dump_' if backup_type == 'sqlite' else 'postgres_dump_'
        
        backups = []
        for filename in os.listdir(self.backup_dir):
            if filename.startswith(prefix):
                filepath = os.path.join(self.backup_dir, filename)
                backups.append((filepath, os.path.getmtime(filepath)))
        
        backups.sort(key=lambda x: x[1], reverse=True)
        
        # Manter apenas os últimos N backups
        for filepath, _ in backups[self.max_backups:]:
            try:
                os.remove(filepath)
                print(f"🗑️  Backup antigo removido: {os.path.basename(filepath)}")
            except:
                pass
    
    def get_stats(self):
        """Retorna estatísticas sobre os backups"""
        backups = self.list_backups()
        
        sqlite_backups = [b for b in backups if b['type'] == 'sqlite']
        postgres_backups = [b for b in backups if b['type'] == 'postgresql']
        
        return {
            'total_backups': len(backups),
            'sqlite_backups': len(sqlite_backups),
            'postgresql_backups': len(postgres_backups),
            'total_size_mb': round(sum(b['size'] for b in backups) / (1024 * 1024), 2),
            'latest_backup': backups[0] if backups else None,
            'oldest_backup': backups[-1] if backups else None
        }


# Criar instância global para usar em toda a aplicação
backup_manager = DatabaseBackupManager()
