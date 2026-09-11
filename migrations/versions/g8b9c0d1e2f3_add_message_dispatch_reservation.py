"""add message dispatch reservation fields

Revision ID: g8b9c0d1e2f3
Revises: f7a8b9c0d1e2
Create Date: 2026-09-11 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = 'g8b9c0d1e2f3'
down_revision = 'f7a8b9c0d1e2'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'message_dispatch',
        sa.Column('reserved_at', sa.DateTime(), nullable=True),
    )
    op.create_index(
        'ix_dispatch_reservada',
        'message_dispatch',
        ['status', 'reserved_at'],
        unique=False,
    )


def downgrade():
    op.execute(
        "UPDATE message_dispatch "
        "SET status = 'pendente' "
        "WHERE status = 'reservada'"
    )
    op.drop_index(
        'ix_dispatch_reservada',
        table_name='message_dispatch',
    )
    op.drop_column('message_dispatch', 'reserved_at')