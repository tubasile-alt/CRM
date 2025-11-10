"""
Sistema de Backup Seguro de Dados
Cria backups automáticos do banco de dados com compressão e timestamping
"""
import os
import shutil
import gzip
from datetime import datetime
import json

class BackupManager:
    """Gerenciador de backups do banco de dados"""
    
    def __init__(self, db_path='instance/medcrm.db', backup_dir='backups'):
        self.db_path = db_path
        self.backup_dir = backup_dir
        self.max_backups = 30  # Manter últimos 30 backups
        
        # Criar diretório de backups se não existir
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
    
    def create_backup(self, compress=True):
        """
        Cria um backup do banco de dados
        
        Args:
            compress: Se True, comprime o backup com gzip
            
        Returns:
            str: Caminho do arquivo de backup criado
        """
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"Banco de dados não encontrado: {self.db_path}")
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f'medcrm_backup_{timestamp}.db'
        backup_path = os.path.join(self.backup_dir, backup_name)
        
        # Copiar banco de dados
        shutil.copy2(self.db_path, backup_path)
        
        # Comprimir se solicitado
        if compress:
            compressed_path = backup_path + '.gz'
            with open(backup_path, 'rb') as f_in:
                with gzip.open(compressed_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            os.remove(backup_path)  # Remover arquivo não comprimido
            backup_path = compressed_path
        
        # Registrar backup
        self._log_backup(backup_path)
        
        # Limpar backups antigos
        self._cleanup_old_backups()
        
        return backup_path
    
    def _log_backup(self, backup_path):
        """Registra informações sobre o backup"""
        log_file = os.path.join(self.backup_dir, 'backup_log.json')
        
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'file': os.path.basename(backup_path),
            'size': os.path.getsize(backup_path),
            'compressed': backup_path.endswith('.gz')
        }
        
        logs = []
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                logs = json.load(f)
        
        logs.append(log_entry)
        
        with open(log_file, 'w') as f:
            json.dump(logs, f, indent=2)
    
    def _cleanup_old_backups(self):
        """Remove backups antigos, mantendo apenas os mais recentes"""
        backups = []
        for filename in os.listdir(self.backup_dir):
            if filename.startswith('medcrm_backup_') and (filename.endswith('.db') or filename.endswith('.db.gz')):
                filepath = os.path.join(self.backup_dir, filename)
                backups.append((filepath, os.path.getmtime(filepath)))
        
        # Ordenar por data de modificação (mais recente primeiro)
        backups.sort(key=lambda x: x[1], reverse=True)
        
        # Remover backups excedentes
        for filepath, _ in backups[self.max_backups:]:
            os.remove(filepath)
    
    def restore_backup(self, backup_file):
        """
        Restaura um backup
        
        Args:
            backup_file: Nome do arquivo de backup ou caminho completo
            
        Returns:
            bool: True se restaurado com sucesso
        """
        # Encontrar arquivo de backup
        if not os.path.isabs(backup_file):
            backup_file = os.path.join(self.backup_dir, backup_file)
        
        if not os.path.exists(backup_file):
            raise FileNotFoundError(f"Backup não encontrado: {backup_file}")
        
        # Criar backup do estado atual antes de restaurar
        current_backup = self.create_backup(compress=True)
        print(f"Backup do estado atual criado: {current_backup}")
        
        # Descomprimir se necessário
        if backup_file.endswith('.gz'):
            temp_file = backup_file[:-3]  # Remover .gz
            with gzip.open(backup_file, 'rb') as f_in:
                with open(temp_file, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            backup_file = temp_file
        
        # Restaurar backup
        shutil.copy2(backup_file, self.db_path)
        
        # Remover arquivo temporário se foi descomprimido
        if backup_file.endswith('.db') and not backup_file.startswith(self.backup_dir):
            os.remove(backup_file)
        
        return True
    
    def list_backups(self):
        """
        Lista todos os backups disponíveis
        
        Returns:
            list: Lista de dicionários com informações dos backups
        """
        backups = []
        for filename in os.listdir(self.backup_dir):
            if filename.startswith('medcrm_backup_') and (filename.endswith('.db') or filename.endswith('.db.gz')):
                filepath = os.path.join(self.backup_dir, filename)
                backups.append({
                    'filename': filename,
                    'path': filepath,
                    'size': os.path.getsize(filepath),
                    'modified': datetime.fromtimestamp(os.path.getmtime(filepath)),
                    'compressed': filename.endswith('.gz')
                })
        
        # Ordenar por data (mais recente primeiro)
        backups.sort(key=lambda x: x['modified'], reverse=True)
        
        return backups
    
    def get_backup_stats(self):
        """
        Retorna estatísticas sobre os backups
        
        Returns:
            dict: Estatísticas dos backups
        """
        backups = self.list_backups()
        
        if not backups:
            return {
                'count': 0,
                'total_size': 0,
                'latest': None,
                'oldest': None
            }
        
        total_size = sum(b['size'] for b in backups)
        
        return {
            'count': len(backups),
            'total_size': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'latest': backups[0],
            'oldest': backups[-1]
        }
