"""add message dispatch status audit

Revision ID: i0d1e2f3a4b5
Revises: h9c0d1e2f3a4
Create Date: 2026-09-11 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = 'i0d1e2f3a4b5'
down_revision = 'h9c0d1e2f3a4'
branch_labels = None
depends_on = None


def upgrade():
    if sa.inspect(op.get_bind()).has_table('message_dispatch_status_audit'):
        return

    op.create_table(
        'message_dispatch_status_audit',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('dispatch_id', sa.Integer(), nullable=True),
        sa.Column('previous_status', sa.String(length=50), nullable=True),
        sa.Column('new_status', sa.String(length=20), nullable=False),
        sa.Column('actor', sa.String(length=100), nullable=False),
        sa.Column('reason', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ['dispatch_id'],
            ['message_dispatch.id'],
            ondelete='SET NULL',
        ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(
        op.f('ix_message_dispatch_status_audit_dispatch_id'),
        'message_dispatch_status_audit',
        ['dispatch_id'],
        unique=False,
    )


def downgrade():
    if not sa.inspect(op.get_bind()).has_table('message_dispatch_status_audit'):
        return

    op.drop_index(
        op.f('ix_message_dispatch_status_audit_dispatch_id'),
        table_name='message_dispatch_status_audit',
    )
    op.drop_table('message_dispatch_status_audit')