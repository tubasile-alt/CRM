"""add consultation finalization fields

Revision ID: f1c2d3e4b5a6
Revises: e8a1b2c3d4e5
Create Date: 2026-03-18 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = 'f1c2d3e4b5a6'
down_revision = 'e8a1b2c3d4e5'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('appointment', sa.Column('consultation_started_at', sa.DateTime(), nullable=True))
    op.add_column('appointment', sa.Column('finalized_at', sa.DateTime(), nullable=True))
    op.add_column('appointment', sa.Column('is_finalized', sa.Boolean(), nullable=True))

    op.add_column('note', sa.Column('finalized_at', sa.DateTime(), nullable=True))
    op.add_column('note', sa.Column('is_finalized', sa.Boolean(), nullable=True))

    op.execute("UPDATE appointment SET is_finalized = FALSE WHERE is_finalized IS NULL")
    op.execute("UPDATE note SET is_finalized = FALSE WHERE is_finalized IS NULL")

    op.execute(
        """
        UPDATE note n
        SET is_finalized = TRUE,
            finalized_at = COALESCE(n.finalized_at, n.created_at)
        WHERE n.note_type = 'conduta'
          AND (
                n.consultation_duration IS NOT NULL
                OR COALESCE(n.content, '') = '[Conduta registrada via procedimentos]'
                OR EXISTS (SELECT 1 FROM indication i WHERE i.note_id = n.id)
                OR EXISTS (SELECT 1 FROM cosmetic_procedure_plan cpp WHERE cpp.note_id = n.id)
                OR EXISTS (SELECT 1 FROM hair_transplant ht WHERE ht.note_id = n.id)
          )
        """
    )

    op.execute(
        """
        UPDATE appointment a
        SET is_finalized = TRUE,
            finalized_at = COALESCE(
                a.finalized_at,
                (
                    SELECT MAX(COALESCE(n.finalized_at, n.created_at))
                    FROM note n
                    WHERE n.appointment_id = a.id
                      AND n.is_finalized = TRUE
                ),
                a.consultation_date,
                a.start_time
            )
        WHERE EXISTS (
            SELECT 1
            FROM note n
            WHERE n.appointment_id = a.id
              AND n.is_finalized = TRUE
        )
           OR a.status = 'atendido'
        """
    )

    op.alter_column('appointment', 'is_finalized', nullable=False)
    op.alter_column('note', 'is_finalized', nullable=False)


def downgrade():
    op.drop_column('note', 'is_finalized')
    op.drop_column('note', 'finalized_at')

    op.drop_column('appointment', 'is_finalized')
    op.drop_column('appointment', 'finalized_at')
    op.drop_column('appointment', 'consultation_started_at')
