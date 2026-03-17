"""finalize procedure execution d3

Revision ID: d3f1a9c2b7e4
Revises: c7d2a4b1f9d0
Create Date: 2026-03-17 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = 'd3f1a9c2b7e4'
down_revision = 'c7d2a4b1f9d0'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('procedure_execution', sa.Column('execution_status', sa.String(length=20), nullable=True))
    op.add_column('procedure_execution', sa.Column('idempotency_key', sa.String(length=100), nullable=True))
    op.add_column('procedure_execution', sa.Column('created_by', sa.Integer(), nullable=True))
    op.add_column('procedure_execution', sa.Column('updated_by', sa.Integer(), nullable=True))
    op.add_column('procedure_execution', sa.Column('updated_at', sa.DateTime(), nullable=True))

    op.execute("""
        UPDATE procedure_execution
        SET execution_status = CASE WHEN was_performed THEN 'realizada' ELSE 'agendada' END,
            updated_at = COALESCE(created_at, NOW())
        WHERE execution_status IS NULL
    """)

    op.alter_column('procedure_execution', 'execution_status', nullable=False)
    op.create_index('ix_procedure_execution_execution_status', 'procedure_execution', ['execution_status'], unique=False)
    op.create_index('ix_procedure_execution_idempotency_key', 'procedure_execution', ['idempotency_key'], unique=True)
    op.create_index('ix_procedure_execution_updated_at', 'procedure_execution', ['updated_at'], unique=False)
    op.create_index('ix_procedure_execution_created_by', 'procedure_execution', ['created_by'], unique=False)
    op.create_index('ix_procedure_execution_updated_by', 'procedure_execution', ['updated_by'], unique=False)

    op.create_foreign_key('fk_procedure_execution_created_by_user', 'procedure_execution', 'user', ['created_by'], ['id'])
    op.create_foreign_key('fk_procedure_execution_updated_by_user', 'procedure_execution', 'user', ['updated_by'], ['id'])

    op.execute("ALTER TABLE procedure_execution ADD CONSTRAINT ck_procedure_execution_status CHECK (execution_status IN ('agendada','realizada','cancelada','faltou'))")
    op.execute("ALTER TABLE procedure_execution ADD CONSTRAINT ck_procedure_followup_status CHECK (followup_status IN ('pendente','contatado','agendado','sem_resposta'))")
    op.execute("ALTER TABLE procedure_execution ADD CONSTRAINT ck_procedure_charged_nonnegative CHECK (charged_value IS NULL OR charged_value >= 0)")

    op.create_index('ix_execution_plan_performed_desc', 'procedure_execution', ['plan_id', 'performed_date'])
    op.create_index('ix_execution_followup_status_date', 'procedure_execution', ['followup_status', 'followup_date'])
    op.create_index('ix_execution_status_scheduled_date', 'procedure_execution', ['execution_status', 'scheduled_date'])

    op.execute("ALTER TABLE cosmetic_procedure_plan ADD CONSTRAINT ck_cosmetic_plan_status CHECK (status IN ('ativo','pausado','concluido','cancelado'))")
    op.drop_column('cosmetic_procedure_plan', 'was_performed')
    op.drop_column('cosmetic_procedure_plan', 'performed_date')


def downgrade():
    op.add_column('cosmetic_procedure_plan', sa.Column('performed_date', sa.DateTime(), nullable=True))
    op.add_column('cosmetic_procedure_plan', sa.Column('was_performed', sa.Boolean(), nullable=True))
    op.execute("UPDATE cosmetic_procedure_plan SET was_performed = FALSE WHERE was_performed IS NULL")
    op.alter_column('cosmetic_procedure_plan', 'was_performed', nullable=False)
    op.execute("ALTER TABLE cosmetic_procedure_plan DROP CONSTRAINT IF EXISTS ck_cosmetic_plan_status")

    op.drop_index('ix_execution_status_scheduled_date', table_name='procedure_execution')
    op.drop_index('ix_execution_followup_status_date', table_name='procedure_execution')
    op.drop_index('ix_execution_plan_performed_desc', table_name='procedure_execution')

    op.execute("ALTER TABLE procedure_execution DROP CONSTRAINT IF EXISTS ck_procedure_charged_nonnegative")
    op.execute("ALTER TABLE procedure_execution DROP CONSTRAINT IF EXISTS ck_procedure_followup_status")
    op.execute("ALTER TABLE procedure_execution DROP CONSTRAINT IF EXISTS ck_procedure_execution_status")

    op.drop_constraint('fk_procedure_execution_updated_by_user', 'procedure_execution', type_='foreignkey')
    op.drop_constraint('fk_procedure_execution_created_by_user', 'procedure_execution', type_='foreignkey')

    op.drop_index('ix_procedure_execution_updated_by', table_name='procedure_execution')
    op.drop_index('ix_procedure_execution_created_by', table_name='procedure_execution')
    op.drop_index('ix_procedure_execution_updated_at', table_name='procedure_execution')
    op.drop_index('ix_procedure_execution_idempotency_key', table_name='procedure_execution')
    op.drop_index('ix_procedure_execution_execution_status', table_name='procedure_execution')

    op.drop_column('procedure_execution', 'updated_at')
    op.drop_column('procedure_execution', 'updated_by')
    op.drop_column('procedure_execution', 'created_by')
    op.drop_column('procedure_execution', 'idempotency_key')
    op.drop_column('procedure_execution', 'execution_status')
