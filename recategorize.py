"""Recategoriza medicamentos com base em nome + marca + tipo."""
from app import app, db
from models import Medication

RULES = [
    # Dermatologia - Acne
    (lambda n,p: 'acne' in n or 'adapaleno' in n or 'benzoil' in n or 'peroxido' in n, 'acne', ['acne']),
    # Dermatologia - Retinoides
    (lambda n,p: 'retinol' in n or 'retinal' in n or 'tretinoin' in n or 'retrinal' in n or 'isotretinoin' in n, 'retinoides', ['acne','anti-envelhecimento']),
    # Protetor solar
    (lambda n,p: 'fps' in n or 'sun' in n or 'episol' in n or 'photoderm' in n or ' photoderm' in n, 'protecao solar', ['protecao solar']),
    # Hidratante / Emoliente
    (lambda n,p: 'hidratante' in n or 'aquaphor' in n or 'emoliente' in n or 'epidrat' in n or 'ph5' in n or 'loção' in n, 'emoliente', ['hidratacao']),
    # Anti-envelhecimento / Anti-idade
    (lambda n,p: 'age' in n or 'hyaluron' in n or 'collagen' in n or 'anti-idade' in n or 'antienvelhecimento' in n or 'ferulic' in n or 'resveratrol' in n or 'peptide' in n, 'anti-envelhecimento', ['anti-envelhecimento']),
    # Clareador / Anti-pigmento
    (lambda n,p: 'anti-pigment' in n or 'clareador' in n or 'melasma' in n or 'mancha' in n or 'discoloration' in n or 'pigment' in n, 'clareador', ['melasma','mancha']),
    # Ácido
    (lambda n,p: any(a in n for a in ['ácido','acido','glycolic','salicylic','mandelic','lactic','azelaic','ferulic']), 'acido', ['pele']),
    # Vitamina C
    (lambda n,p: 'vitamin c' in n or 'vit c' in n or 'pure c' in n or 'flavo c' in n, 'vitamina c', ['anti-envelhecimento','clareamento']),
    # Vitaminas gerais
    (lambda n,p: 'vitamin' in n or 'biotin' in n or 'zinco' in n, 'vitamina', ['geral']),
    # Controle de oleosidade / Pore
    (lambda n,p: 'oil control' in n or 'sebo' in n or 'pore' in n or 'matific' in n or 'mat' in n, 'oleosidade', ['seborreia']),
    # Shampoo / Capilar
    (lambda n,p: 'shampoo' in n or 'condicionador' in n or 'minoxidil' in n or 'hair' in n or 'capil' in n or 'dercos' in n or 'kerasolution' in n or 'skinceuticals' in n or 'grow' in n, 'capilar', ['alopecia']),
    # Limpeza / Sabonete
    (lambda n,p: 'limpeza' in n or 'sabonete' in n or 'gel de' in n or 'moussant' in n or 'espuma' in n or 'micelar' in n, 'limpeza', ['pele']),
    # Calmante / Sensível
    (lambda n,p: 'calm' in n or 'sensibio' in n or 'tolérance' in n or 'cicaplast' in n or 'restoraderm' in n or 'repair' in n, 'calmante', ['dermatite','sensivel']),
    # Antifúngico
    (lambda n,p: 'miconazol' in n or 'ciclopirox' in n or 'nystatin' in n or 'ketoconazol' in n or 'itraconazol' in n or 'terbinafin' in n or 'fluconazol' in n, 'antifungico', ['micose']),
    # Antibiótico
    (lambda n,p: any(a in n for a in ['clindamicina','eritromicina','doxiciclina','minociclina','azitromicina','mupirocina','fusidico','tetraciclina']), 'antibiotico', ['infeccao']),
    # Imunomodulador
    (lambda n,p: 'pimecrolimus' in n or 'tacrolimus' in n or 'imiquimod' in n, 'imunomodulador', ['dermatite']),
    # Corticoide
    (lambda n,p: any(a in n for a in ['betametasona','triancinolona','mometasona','hidrocortisona','dexametasona']), 'corticoide', ['inflamacao']),
    # Suplemento
    (lambda n,p: 'colágeno' in n or 'omega' in n or 'ácido hialurônico' in n or 'suplemento' in n or 'ferro' in n or 'magnesio' in n or 'cálcio' in n, 'suplemento', ['geral']),
    # Analgésico
    (lambda n,p: any(a in n for a in ['dipirona','paracetamol','ibuprofeno','tramadol']), 'analgesico', ['dor']),
    # Oral systemico
    (lambda n,p: 'mg' in n and not 'em mg' in n, 'oral', ['geral']),
]

def recategorize():
    with app.app_context():
        meds = Medication.query.filter_by(categoria='nao-categorizado').all()
        updated = 0
        for m in meds:
            n = m.name.lower()
            p = (m.purpose or '').lower()
            for rule_fn, cat, inds in RULES:
                if rule_fn(n, p):
                    m.categoria = cat
                    m.indicacoes = inds
                    updated += 1
                    break
        db.session.commit()
        
        # Stats
        from sqlalchemy import func
        cats = db.session.query(Medication.categoria, func.count(Medication.id)).group_by(Medication.categoria).all()
        print(f'Updated {updated} medications.')
        print('\nCategories:')
        for cat, cnt in sorted(cats, key=lambda x: -x[1]):
            print(f'  {cat}: {cnt}')

if __name__ == '__main__':
    recategorize()
