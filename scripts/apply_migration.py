import sys
sys.path.insert(0, '/home/runner/workspace')
from app import app
from models import db
from sqlalchemy import text

with app.app_context():
    # Aditiva: adiciona colunas se não existirem
    q = text("""
        ALTER TABLE medications
        ADD COLUMN IF NOT EXISTS categoria VARCHAR(100),
        ADD COLUMN IF NOT EXISTS indicacoes JSON,
        ADD COLUMN IF NOT EXISTS etiqueta_revisada BOOLEAN DEFAULT FALSE
    """)
    db.session.execute(q)
    db.session.commit()
    print("Migração aplicada: categoria, indicacoes, etiqueta_revisada")
