"""create push subscription table

Revision ID: b4c2d8e9f0a1
Revises: a3d4e5f6b7c8
Create Date: 2026-06-02 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = 'b4c2d8e9f0a1'
down_revision = 'a3d4e5f6b7c8'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'push_subscription',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('endpoint', sa.Text(), nullable=False),
        sa.Column('p256dh', sa.Text(), nullable=False),
        sa.Column('auth', sa.Text(), nullable=False),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('last_seen_at', sa.DateTime(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.ForeignKeyConstraint(['user_id'], ['user.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'endpoint', name='uq_push_subscription_user_endpoint'),
    )
    op.create_index('ix_push_subscription_user_id', 'push_subscription', ['user_id'], unique=False)
    op.create_index('idx_push_subscription_user_active', 'push_subscription', ['user_id', 'is_active'], unique=False)


def downgrade():
    op.drop_index('idx_push_subscription_user_active', table_name='push_subscription')
    op.drop_index('ix_push_subscription_user_id', table_name='push_subscription')
    op.drop_table('push_subscription')
