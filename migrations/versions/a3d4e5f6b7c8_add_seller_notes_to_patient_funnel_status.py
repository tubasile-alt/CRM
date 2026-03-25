"""add seller notes to patient funnel status

Revision ID: a3d4e5f6b7c8
Revises: f1c2d3e4b5a6
Create Date: 2026-03-25 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = 'a3d4e5f6b7c8'
down_revision = 'f1c2d3e4b5a6'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('patient_funnel_status', sa.Column('seller_notes', sa.Text(), nullable=True))


def downgrade():
    op.drop_column('patient_funnel_status', 'seller_notes')
