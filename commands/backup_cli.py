"""
CLI para Backup e Restauração de Banco de Dados
Use: python commands/backup_cli.py [comando] [opções]
"""

import click
import os
from datetime import datetime
from utils.database_backup import backup_manager


@click.group()
def cli():
    """Sistema de Backup do Banco de Dados"""
    pass


@cli.command()
@click.option('--type', 'backup_type', type=click.Choice(['sqlite', 'postgresql', 'both']), default='both')
def backup(backup_type):
    """Cria backup do banco de dados"""
    click.echo("🔄 Iniciando backup do banco de dados...\n")
    
    try:
        if backup_type in ['sqlite', 'both']:
            click.echo("📦 Backup SQLite...")
            sqlite_backup = backup_manager.backup_sqlite()
            click.echo(f"✅ {sqlite_backup}\n")
        
        if backup_type in ['postgresql', 'both']:
            click.echo("📦 Backup PostgreSQL...")
            database_url = os.environ.get('DATABASE_URL')
            if not database_url:
                click.echo("⚠️  DATABASE_URL não configurada - pulando PostgreSQL\n")
            else:
                postgres_backup = backup_manager.backup_postgresql(database_url)
                click.echo(f"✅ {postgres_backup}\n")
        
        # Mostrar estatísticas
        stats = backup_manager.get_stats()
        click.echo("📊 Estatísticas de Backup:")
        click.echo(f"   Total de backups: {stats['total_backups']}")
        click.echo(f"   SQLite: {stats['sqlite_backups']}")
        click.echo(f"   PostgreSQL: {stats['postgresql_backups']}")
        click.echo(f"   Espaço total: {stats['total_size_mb']} MB\n")
        
    except Exception as e:
        click.echo(f"❌ Erro: {e}", err=True)
        exit(1)


@cli.command()
def list():
    """Lista todos os backups disponíveis"""
    backups = backup_manager.list_backups()
    
    if not backups:
        click.echo("Nenhum backup encontrado")
        return
    
    click.echo("📋 Backups Disponíveis:\n")
    for i, backup in enumerate(backups, 1):
        click.echo(f"{i}. {backup['file']}")
        click.echo(f"   Tipo: {backup['type']}")
        click.echo(f"   Tamanho: {backup['size_mb']} MB")
        click.echo(f"   Data: {backup['modified']}\n")


@cli.command()
@click.option('--file', required=True, help='Nome do arquivo de backup')
@click.confirmation_option(prompt='Tem certeza que deseja restaurar?')
def restore(file):
    """Restaura um backup"""
    try:
        click.echo(f"🔄 Restaurando backup: {file}\n")
        backup_manager.restore_sqlite(file)
        click.echo(f"✅ Banco restaurado com sucesso!\n")
    except Exception as e:
        click.echo(f"❌ Erro ao restaurar: {e}", err=True)
        exit(1)


@cli.command()
def stats():
    """Mostra estatísticas dos backups"""
    stats = backup_manager.get_stats()
    
    click.echo("📊 Estatísticas de Backup:\n")
    click.echo(f"Total de backups: {stats['total_backups']}")
    click.echo(f"  - SQLite: {stats['sqlite_backups']}")
    click.echo(f"  - PostgreSQL: {stats['postgresql_backups']}")
    click.echo(f"Espaço total: {stats['total_size_mb']} MB\n")
    
    if stats['latest_backup']:
        click.echo(f"Backup mais recente:")
        click.echo(f"  {stats['latest_backup']['file']}")
        click.echo(f"  {stats['latest_backup']['size_mb']} MB")
        click.echo(f"  {stats['latest_backup']['modified']}\n")


if __name__ == '__main__':
    cli()
