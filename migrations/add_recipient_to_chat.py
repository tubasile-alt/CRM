#!/usr/bin/env python3
"""
Migration: Adicionar recipient_id ao chat (mensagens direcionadas 1-on-1)

ATENÇÃO: Esta migration RECRIA a tabela chat_message, perdendo o histórico.
Isso é aceitável em desenvolvimento, mas em produção seria necessário migration mais complexa.

Execução:
    python migrations/add_recipient_to_chat.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db

def main():
    print("=" * 70)
    print("Migration: Adicionar recipient_id ao ChatMessage")
    print("ATENÇÃO: Esta operação irá RECRIAR a tabela chat_message!")
    print("=" * 70)
    
    with app.app_context():
        print("\n[1/3] Removendo tabela chat_message antiga...")
        try:
            db.session.execute(db.text("DROP TABLE IF EXISTS chat_message"))
            db.session.commit()
            print("✅ Tabela chat_message removida")
        except Exception as e:
            print(f"❌ Erro ao remover tabela: {e}")
            return 1
        
        print("\n[2/3] Criando nova tabela chat_message com recipient_id...")
        try:
            db.create_all()
            print("✅ Tabela chat_message criada com sucesso!")
            print("\nEstrutura da tabela:")
            print("  - id (PK)")
            print("  - sender_id (FK -> user.id)")
            print("  - recipient_id (FK -> user.id) [NOVO]")
            print("  - message (TEXT)")
            print("  - created_at (TIMESTAMP)")
            print("  - read (BOOLEAN, deprecated)")
        except Exception as e:
            print(f"❌ Erro ao criar tabela: {e}")
            return 1
        
        print("\n[3/3] Verificando integridade...")
        try:
            result = db.session.execute(db.text(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='chat_message'"
            ))
            if result.fetchone():
                print("✅ Tabela chat_message existe e está pronta!")
            else:
                print("⚠️  Tabela não foi criada corretamente.")
                return 1
        except Exception as e:
            print(f"❌ Erro ao verificar tabela: {e}")
            return 1
        
        print("\n" + "=" * 70)
        print("Migration concluída com sucesso!")
        print("=" * 70)
        print("\nMudanças:")
        print("  ✅ Chat agora é 1-on-1 (mensagens direcionadas)")
        print("  ✅ Campo recipient_id adicionado")
        print("  ✅ Histórico de mensagens antigas removido")
        print("\nPróximos passos:")
        print("  1. Reiniciar o servidor Flask")
        print("  2. Testar seletor de destinatário no chat")
        print("  3. Verificar que mensagens são direcionadas corretamente")
        
        return 0

if __name__ == '__main__':
    exit(main())
