
import pandas as pd
import os
import json
from app import app, db
from models import Medication

def import_medications():
    file_path = 'attached_assets/medicamentos_relatorio_20260202_144959_1770045250176.xlsx'
    if not os.path.exists(file_path):
        print(f"Arquivo não encontrado: {file_path}")
        return

    try:
        df = pd.read_excel(file_path)
        
        # Mapeamento de colunas baseado no JSON anterior:
        # Nome, Tipo, Posologia, Finalidade, Marca
        
        with app.app_context():
            count = 0
            for _, row in df.iterrows():
                name = str(row['Nome']).strip()
                if not name or name == 'nan':
                    continue
                
                # Verificar se já existe
                existing = Medication.query.filter_by(name=name).first()
                if existing:
                    continue
                
                med = Medication(
                    name=name,
                    category=str(row['Tipo']).lower() if pd.notna(row['Tipo']) else 'topical',
                    default_instructions=str(row['Posologia']) if pd.notna(row['Posologia']) else '',
                    brand=str(row['Marca']) if pd.notna(row['Marca']) else None,
                    description=str(row['Finalidade']) if pd.notna(row['Finalidade']) else None
                )
                db.session.add(med)
                count += 1
                
                if count % 100 == 0:
                    db.session.commit()
            
            db.session.commit()
            print(f"Sucesso: {count} medicamentos importados.")

    except Exception as e:
        print(f"Erro na importação: {str(e)}")

if __name__ == "__main__":
    import_medications()
