"""add procedure execution d1

Revision ID: c7d2a4b1f9d0
Revises: 9e1f0a6a3d11
Create Date: 2026-03-16 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c7d2a4b1f9d0'
down_revision = '9e1f0a6a3d11'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('cosmetic_procedure_plan', sa.Column('status', sa.String(length=20), nullable=True))
    op.execute("UPDATE cosmetic_procedure_plan SET status = 'ativo' WHERE status IS NULL")
    op.alter_column('cosmetic_procedure_plan', 'status', nullable=False)
    op.create_index(op.f('ix_cosmetic_procedure_plan_status'), 'cosmetic_procedure_plan', ['status'], unique=False)

    op.create_table(
        'procedure_execution',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('plan_id', sa.Integer(), nullable=False),
        sa.Column('scheduled_date', sa.DateTime(), nullable=True),
        sa.Column('performed_date', sa.DateTime(), nullable=True),
        sa.Column('was_performed', sa.Boolean(), nullable=False),
        sa.Column('charged_value', sa.Numeric(10, 2), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('followup_date', sa.DateTime(), nullable=True),
        sa.Column('followup_status', sa.String(length=20), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['plan_id'], ['cosmetic_procedure_plan.id']),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_index(op.f('ix_procedure_execution_plan_id'), 'procedure_execution', ['plan_id'], unique=False)
    op.create_index(op.f('ix_procedure_execution_scheduled_date'), 'procedure_execution', ['scheduled_date'], unique=False)
    op.create_index(op.f('ix_procedure_execution_performed_date'), 'procedure_execution', ['performed_date'], unique=False)
    op.create_index(op.f('ix_procedure_execution_was_performed'), 'procedure_execution', ['was_performed'], unique=False)
    op.create_index(op.f('ix_procedure_execution_followup_date'), 'procedure_execution', ['followup_date'], unique=False)
    op.create_index(op.f('ix_procedure_execution_followup_status'), 'procedure_execution', ['followup_status'], unique=False)
    op.create_index(op.f('ix_procedure_execution_created_at'), 'procedure_execution', ['created_at'], unique=False)

    op.execute(
        """
        INSERT INTO procedure_execution (
            plan_id,
            scheduled_date,
            performed_date,
            was_performed,
            charged_value,
            notes,
            followup_date,
            followup_status,
            created_at
        )
        SELECT
            p.id,
            p.performed_date,
            p.performed_date,
            TRUE,
            COALESCE(p.final_budget, p.planned_value),
            p.observations,
            NULL,
            'pendente',
            COALESCE(p.created_at, NOW())
        FROM cosmetic_procedure_plan p
        WHERE p.was_performed = TRUE
          AND p.performed_date IS NOT NULL
        """
    )


def downgrade():
    op.drop_index(op.f('ix_procedure_execution_created_at'), table_name='procedure_execution')
    op.drop_index(op.f('ix_procedure_execution_followup_status'), table_name='procedure_execution')
    op.drop_index(op.f('ix_procedure_execution_followup_date'), table_name='procedure_execution')
    op.drop_index(op.f('ix_procedure_execution_was_performed'), table_name='procedure_execution')
    op.drop_index(op.f('ix_procedure_execution_performed_date'), table_name='procedure_execution')
    op.drop_index(op.f('ix_procedure_execution_scheduled_date'), table_name='procedure_execution')
    op.drop_index(op.f('ix_procedure_execution_plan_id'), table_name='procedure_execution')
    op.drop_table('procedure_execution')

    op.drop_index(op.f('ix_cosmetic_procedure_plan_status'), table_name='cosmetic_procedure_plan')
    op.drop_column('cosmetic_procedure_plan', 'status')
