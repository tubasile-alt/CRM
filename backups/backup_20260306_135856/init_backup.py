#!/usr/bin/env python3
"""
Script de Inicialização com Backup Automático
Execute antes de iniciar a aplicação: python init_backup.py
"""

import os
import sys
from utils.database_backup import backup_manager

print("🔄 Inicializando sistema de backup...\n")

try:
    # Backup SQLite
    print("📦 Fazendo backup do banco SQLite...")
    sqlite_backup = backup_manager.backup_sqlite()
    print(f"✅ {sqlite_backup}\n")
    
    # Backup PostgreSQL (se configurado)
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        print("📦 Fazendo backup do banco PostgreSQL...")
        try:
            postgres_backup = backup_manager.backup_postgresql(database_url)
            print(f"✅ {postgres_backup}\n")
        except Exception as e:
            print(f"⚠️  PostgreSQL não disponível: {e}\n")
    
    # Mostrar estatísticas
    stats = backup_manager.get_stats()
    print("📊 Status de Backups:")
    print(f"   Total: {stats['total_backups']} backups")
    print(f"   Espaço: {stats['total_size_mb']} MB")
    print(f"   SQLite: {stats['sqlite_backups']}")
    print(f"   PostgreSQL: {stats['postgresql_backups']}\n")
    
    print("✅ Sistema de backup pronto!\n")
    
except Exception as e:
    print(f"❌ Erro ao inicializar backup: {e}\n")
    sys.exit(1)
