"""add plan name and backfill

Revision ID: e8a1b2c3d4e5
Revises: d3f1a9c2b7e4
Create Date: 2026-03-17 00:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = 'e8a1b2c3d4e5'
down_revision = 'd3f1a9c2b7e4'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('cosmetic_procedure_plan', sa.Column('name', sa.String(length=150), nullable=True))

    op.execute(
        """
        UPDATE cosmetic_procedure_plan
        SET name = CONCAT(COALESCE(procedure_name, 'Procedimento'), ' - ', TO_CHAR(COALESCE(created_at, NOW()), 'Mon YYYY'))
        WHERE name IS NULL OR name = ''
        """
    )

    op.alter_column('cosmetic_procedure_plan', 'name', nullable=False)

    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name='cosmetic_procedure_plan' AND column_name='was_performed'
            ) THEN
                INSERT INTO procedure_execution (
                    plan_id,
                    performed_date,
                    was_performed,
                    execution_status,
                    charged_value,
                    notes,
                    followup_status,
                    created_at,
                    updated_at
                )
                SELECT
                    p.id,
                    p.performed_date,
                    TRUE,
                    'realizada',
                    COALESCE(p.final_budget, p.planned_value),
                    p.observations,
                    'pendente',
                    COALESCE(p.created_at, NOW()),
                    COALESCE(p.created_at, NOW())
                FROM cosmetic_procedure_plan p
                WHERE p.was_performed = TRUE
                  AND p.performed_date IS NOT NULL
                  AND NOT EXISTS (
                    SELECT 1 FROM procedure_execution e WHERE e.plan_id = p.id AND e.was_performed = TRUE
                  );

                ALTER TABLE cosmetic_procedure_plan DROP COLUMN was_performed;
                ALTER TABLE cosmetic_procedure_plan DROP COLUMN performed_date;
            END IF;
        END$$;
        """
    )


def downgrade():
    op.add_column('cosmetic_procedure_plan', sa.Column('performed_date', sa.DateTime(), nullable=True))
    op.add_column('cosmetic_procedure_plan', sa.Column('was_performed', sa.Boolean(), nullable=True))
    op.execute("UPDATE cosmetic_procedure_plan SET was_performed = FALSE WHERE was_performed IS NULL")
    op.alter_column('cosmetic_procedure_plan', 'was_performed', nullable=False)
    op.drop_column('cosmetic_procedure_plan', 'name')
