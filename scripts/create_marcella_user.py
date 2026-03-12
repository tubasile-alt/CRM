import os
import sys

ROOT = os.path.dirname(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app import app
from models import User, db


def ensure_marcella():
    with app.app_context():
        user = User.query.filter_by(username='marcella').first()
        if not user:
            user = User(
                username='marcella',
                email='marcella@clinicabasile.local',
                name='Marcella',
                role='secretaria',
                role_clinico='SECRETARY',
            )
            db.session.add(user)

        user.name = 'Marcella'
        user.role = 'secretaria'
        user.role_clinico = 'SECRETARY'
        user.set_password('654321')

        db.session.commit()
        print('Usuária Marcella criada/atualizada com sucesso.')


if __name__ == '__main__':
    ensure_marcella()
