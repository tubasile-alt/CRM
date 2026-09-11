"""add message dispatch attempts

Revision ID: h9c0d1e2f3a4
Revises: g8b9c0d1e2f3
Create Date: 2026-09-11 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = 'h9c0d1e2f3a4'
down_revision = 'g8b9c0d1e2f3'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'message_dispatch',
        sa.Column(
            'attempts',
            sa.Integer(),
            nullable=False,
            server_default='0',
        ),
    )


def downgrade():
    op.drop_column('message_dispatch', 'attempts')