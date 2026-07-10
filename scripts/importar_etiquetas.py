import sys, json, os
sys.path.insert(0, '/home/runner/workspace')

from app import app
from models import db, Medication
import pandas as pd

XLSX_PATH = 'attached_assets/BASE_DE_DADOS_REVISADA_PRESCRICAO_CRM_1783695262020.xlsx'

def normalize(text):
    if pd.isna(text) or text is None:
        return None
    return str(text).strip().lower()

def parse_indicacoes(val):
    if pd.isna(val) or val is None:
        return None
    parts = str(val).replace(',', ';').split(';')
    result = [normalize(p) for p in parts if normalize(p)]
    return result if result else None

def main():
    with app.app_context():
        df = pd.read_excel(XLSX_PATH, sheet_name='Revisão etiquetas')
        total_linhas = len(df)
        atualizados = 0
        nao_encontrados = 0
        ids_nao_encontrados = []

        for _, row in df.iterrows():
            med_id = int(row['ID'])
            cat = normalize(row.get('Categoria sugerida'))
            inds = parse_indicacoes(row.get('Indicações sugeridas'))
            posologia = str(row.get('Propósito (base atual)')).strip() if pd.notna(row.get('Propósito (base atual)')) else None

            med = Medication.query.get(med_id)
            if med:
                med.categoria = cat
                med.indicacoes = inds
                if posologia:
                    med.instructions = posologia
                med.etiqueta_revisada = True
                atualizados += 1
            else:
                nao_encontrados += 1
                ids_nao_encontrados.append((med_id, row.get('Medicamento', '???')))

        db.session.commit()

        # Medicamentos no banco que NÃO estão na planilha
        ids_planilha = set(int(r['ID']) for _, r in df.iterrows())
        todos = Medication.query.all()
        pendentes = [(m.id, m.name) for m in todos if m.id not in ids_planilha]
        # Garantir etiqueta_revisada=False nos pendentes
        for m in todos:
            if m.id not in ids_planilha and m.etiqueta_revisada != False:
                m.etiqueta_revisada = False
        db.session.commit()

        print(f"=== RESUMO IMPORTAÇÃO ===")
        print(f"Linhas na planilha: {total_linhas}")
        print(f"Atualizados: {atualizados}")
        print(f"IDs não encontrados no banco: {nao_encontrados}")
        if ids_nao_encontrados:
            for i, n in ids_nao_encontrados:
                print(f"  - id {i}: {n}")
        print(f"Medicamentos pendentes (sem etiqueta): {len(pendentes)}")
        if pendentes:
            for i, n in pendentes[:20]:
                print(f"  - id {i}: {n}")
            if len(pendentes) > 20:
                print(f"  ... e mais {len(pendentes)-20}")

if __name__ == '__main__':
    main()
