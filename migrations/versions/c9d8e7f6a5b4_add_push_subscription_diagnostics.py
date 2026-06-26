"""add push subscription diagnostics

Revision ID: c9d8e7f6a5b4
Revises: b4c2d8e9f0a1
Create Date: 2026-06-26 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = 'c9d8e7f6a5b4'
down_revision = 'b4c2d8e9f0a1'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('push_subscription', sa.Column('endpoint_partial', sa.String(length=140), nullable=True))
    op.add_column('push_subscription', sa.Column('platform', sa.String(length=40), nullable=True))
    op.add_column('push_subscription', sa.Column('last_test_at', sa.DateTime(), nullable=True))
    op.add_column('push_subscription', sa.Column('last_error', sa.Text(), nullable=True))


def downgrade():
    op.drop_column('push_subscription', 'last_error')
    op.drop_column('push_subscription', 'last_test_at')
    op.drop_column('push_subscription', 'platform')
    op.drop_column('push_subscription', 'endpoint_partial')
