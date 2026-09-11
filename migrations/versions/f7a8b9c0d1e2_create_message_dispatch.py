"""create message dispatch table

Revision ID: f7a8b9c0d1e2
Revises: e2f3a4b5c6d7
Create Date: 2026-09-11 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = 'f7a8b9c0d1e2'
down_revision = 'e2f3a4b5c6d7'
branch_labels = None
depends_on = None


def upgrade():
    # The table may already exist because older development databases used
    # db.create_all(). In that case, keep the existing production-shaped table
    # and only record this revision.
    if sa.inspect(op.get_bind()).has_table('message_dispatch'):
        return

    op.create_table(
        'message_dispatch',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('patient_id', sa.Integer(), nullable=False),
        sa.Column('execution_id', sa.Integer(), nullable=False),
        sa.Column('message_type', sa.String(length=20), nullable=False),
        sa.Column('due_at', sa.Date(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('sent_at', sa.DateTime(), nullable=True),
        sa.Column('last_error', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['execution_id'], ['procedure_execution.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['patient_id'], ['patient.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint(
            'patient_id',
            'message_type',
            'due_at',
            name='ux_dispatch_patient_type_due',
        ),
    )
    op.create_index(
        op.f('ix_message_dispatch_patient_id'),
        'message_dispatch',
        ['patient_id'],
        unique=False,
    )
    op.create_index(
        op.f('ix_message_dispatch_execution_id'),
        'message_dispatch',
        ['execution_id'],
        unique=False,
    )
    op.create_index(
        op.f('ix_message_dispatch_due_at'),
        'message_dispatch',
        ['due_at'],
        unique=False,
    )
    op.create_index(
        'ix_dispatch_due',
        'message_dispatch',
        ['status', 'due_at'],
        unique=False,
    )


def downgrade():
    if not sa.inspect(op.get_bind()).has_table('message_dispatch'):
        return

    op.drop_index('ix_dispatch_due', table_name='message_dispatch')
    op.drop_index(
        op.f('ix_message_dispatch_due_at'),
        table_name='message_dispatch',
    )
    op.drop_index(
        op.f('ix_message_dispatch_execution_id'),
        table_name='message_dispatch',
    )
    op.drop_index(
        op.f('ix_message_dispatch_patient_id'),
        table_name='message_dispatch',
    )
    op.drop_table('message_dispatch')