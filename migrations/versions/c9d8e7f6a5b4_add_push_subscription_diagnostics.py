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
    bind = op.get_bind()
    existing_columns = {
        column['name']
        for column in sa.inspect(bind).get_columns('push_subscription')
    }
    diagnostic_columns = (
        ('endpoint_partial', sa.String(length=140)),
        ('platform', sa.String(length=40)),
        ('last_test_at', sa.DateTime()),
        ('last_error', sa.Text()),
    )

    # Some legacy databases received these columns from the old runtime
    # compatibility helper before the schema entered Alembic. Treat those
    # columns as adopted instead of failing on DuplicateColumn.
    for name, column_type in diagnostic_columns:
        if name not in existing_columns:
            op.add_column(
                'push_subscription',
                sa.Column(name, column_type, nullable=True),
            )


def downgrade():
    op.drop_column('push_subscription', 'last_error')
    op.drop_column('push_subscription', 'last_test_at')
    op.drop_column('push_subscription', 'platform')
    op.drop_column('push_subscription', 'endpoint_partial')
