"""
Migration: Add final_budget to cosmetic_procedure_plan
and previous_transplant fields to hair_transplant
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text

def upgrade(db):
    """Add new columns to cosmetic_procedure_plan and hair_transplant tables"""
    with db.engine.connect() as conn:
        # Add final_budget to cosmetic_procedure_plan
        try:
            conn.execute(text(
                'ALTER TABLE cosmetic_procedure_plan ADD COLUMN final_budget NUMERIC(10, 2)'
            ))
            conn.commit()
            print("✓ Added final_budget column to cosmetic_procedure_plan")
        except Exception as e:
            print(f"Column final_budget may already exist: {e}")
        
        # Add previous_transplant to hair_transplant
        try:
            conn.execute(text(
                "ALTER TABLE hair_transplant ADD COLUMN previous_transplant VARCHAR(10) DEFAULT 'nao'"
            ))
            conn.commit()
            print("✓ Added previous_transplant column to hair_transplant")
        except Exception as e:
            print(f"Column previous_transplant may already exist: {e}")
        
        # Add transplant_location to hair_transplant
        try:
            conn.execute(text(
                'ALTER TABLE hair_transplant ADD COLUMN transplant_location VARCHAR(50)'
            ))
            conn.commit()
            print("✓ Added transplant_location column to hair_transplant")
        except Exception as e:
            print(f"Column transplant_location may already exist: {e}")

def downgrade(db):
    """Remove the added columns"""
    with db.engine.connect() as conn:
        try:
            conn.execute(text('ALTER TABLE cosmetic_procedure_plan DROP COLUMN final_budget'))
            conn.commit()
            print("✓ Removed final_budget column from cosmetic_procedure_plan")
        except Exception as e:
            print(f"Error removing final_budget: {e}")
        
        try:
            conn.execute(text('ALTER TABLE hair_transplant DROP COLUMN previous_transplant'))
            conn.commit()
            print("✓ Removed previous_transplant column from hair_transplant")
        except Exception as e:
            print(f"Error removing previous_transplant: {e}")
        
        try:
            conn.execute(text('ALTER TABLE hair_transplant DROP COLUMN transplant_location'))
            conn.commit()
            print("✓ Removed transplant_location column from hair_transplant")
        except Exception as e:
            print(f"Error removing transplant_location: {e}")

if __name__ == '__main__':
    from app import app
    from models import db
    with app.app_context():
        print("Running migration: add_cosmetic_and_transplant_fields")
        upgrade(db)
        print("Migration completed successfully!")
