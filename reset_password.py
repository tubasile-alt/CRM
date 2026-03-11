#!/usr/bin/env python3
"""
Script para resetar senha de usuários no sistema
Use: python reset_password.py
"""
import sys
from app import app, db
from models import User

def reset_user_password():
    with app.app_context():
        # Procura por email ou username contendo 'erica'
        user = User.query.filter(
            (User.email.ilike('%erica%')) | 
            (User.username.ilike('%erica%'))
        ).first()
        
        if not user:
            print("❌ Usuário 'Erica' não encontrado no banco de dados.")
            print("\nUsuários no sistema:")
            all_users = User.query.all()
            for u in all_users:
                print(f"  - ID {u.id}: {u.name} ({u.email}) | Role: {u.role}")
            return False
        
        print(f"✅ Usuário encontrado: {user.name} ({user.email})")
        print(f"   ID: {user.id} | Role: {user.role}")
        
        # Reseta para senha padrão
        nova_senha = "123456"
        user.set_password(nova_senha)
        db.session.commit()
        
        print(f"\n✅ Senha resetada com sucesso!")
        print(f"   Email: {user.email}")
        print(f"   Nova Senha: {nova_senha}")
        print(f"\nAgora você consegue fazer login com essas credenciais.")
        
        return True

if __name__ == '__main__':
    reset_user_password()
