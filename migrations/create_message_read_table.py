#!/usr/bin/env python3
"""
Migration: Criar tabela MessageRead para rastreamento de leituras por usuário

Este script cria a nova tabela 'message_read' para resolver o bug onde
o campo 'read' em ChatMessage era global (afetava todos os usuários).

Execução:
    python migrations/create_message_read_table.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import MessageRead

def main():
    print("=" * 60)
    print("Migration: Criar tabela MessageRead")
    print("=" * 60)
    
    with app.app_context():
        print("\n[1/2] Criando tabela message_read...")
        try:
            db.create_all()
            print("✅ Tabela message_read criada com sucesso!")
            print("\nEstrutura da tabela:")
            print("  - id (PK)")
            print("  - message_id (FK -> chat_message.id) [indexed]")
            print("  - user_id (FK -> user.id) [indexed]")
            print("  - read_at (timestamp)")
            print("  - UNIQUE(message_id, user_id)")
            print("  - INDEX(message_id, user_id)")
        except Exception as e:
            print(f"❌ Erro ao criar tabela: {e}")
            return 1
        
        print("\n[2/2] Verificando integridade...")
        try:
            result = db.session.execute(db.text(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='message_read'"
            ))
            if result.fetchone():
                print("✅ Tabela message_read existe e está pronta para uso!")
            else:
                print("⚠️  Tabela não foi criada corretamente.")
                return 1
        except Exception as e:
            print(f"❌ Erro ao verificar tabela: {e}")
            return 1
        
        print("\n" + "=" * 60)
        print("Migration concluída com sucesso!")
        print("=" * 60)
        print("\nPróximos passos:")
        print("  1. Reiniciar o servidor Flask")
        print("  2. Testar funcionalidade de badge de mensagens não lidas")
        print("  3. Verificar que cada usuário vê seu próprio contador")
        print("\nNota: Mensagens antigas não foram migradas (consideradas lidas).")
        
        return 0

if __name__ == '__main__':
    exit(main())
