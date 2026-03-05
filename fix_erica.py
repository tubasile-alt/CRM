from app import app, db
from models import User
from werkzeug.security import generate_password_hash

def fix_erica():
    with app.app_context():
        # Erica (ID 10 e 12 no log anterior, vamos garantir em todos com esse nome)
        users = User.query.filter(User.name.ilike('%erica%')).all()
        if not users:
            print("Usuário Erica não encontrado pelo nome.")
            return
            
        for u in users:
            u.username = 'erica'
            u.password_hash = generate_password_hash('1234')
            u.role = 'secretaria'
            u.role_clinico = 'SECRETARY'
            print(f"Atualizado: {u.name} (ID: {u.id}) -> login: erica, senha: 1234")
            
        db.session.commit()
        print("Alterações salvas com sucesso.")

if __name__ == '__main__':
    fix_erica()
