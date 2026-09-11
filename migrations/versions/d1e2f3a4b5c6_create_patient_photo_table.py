"""create persistent patient photo table

Revision ID: d1e2f3a4b5c6
Revises: c9d8e7f6a5b4
Create Date: 2026-06-30 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = 'd1e2f3a4b5c6'
down_revision = 'c9d8e7f6a5b4'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if inspector.has_table('patient_photo'):
        columns = {
            column['name']
            for column in inspector.get_columns('patient_photo')
        }
        required_columns = {
            'id',
            'patient_id',
            'data',
            'mime_type',
            'updated_at',
        }
        missing_columns = required_columns - columns
        if missing_columns:
            raise RuntimeError(
                'patient_photo já existe, mas está incompleta; '
                f'faltam: {sorted(missing_columns)}'
            )

        has_unique_patient_index = any(
            index.get('unique') and index.get('column_names') == ['patient_id']
            for index in inspector.get_indexes('patient_photo')
        )
        if not has_unique_patient_index:
            raise RuntimeError(
                'patient_photo já existe, mas não possui unicidade em patient_id'
            )
        return

    op.create_table(
        'patient_photo',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('patient_id', sa.Integer(), nullable=False),
        sa.Column('data', sa.LargeBinary(), nullable=False),
        sa.Column('mime_type', sa.String(length=50), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['patient_id'], ['patient.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(
        op.f('ix_patient_photo_patient_id'),
        'patient_photo',
        ['patient_id'],
        unique=True,
    )


def downgrade():
    op.drop_index(op.f('ix_patient_photo_patient_id'), table_name='patient_photo')
    op.drop_table('patient_photo')
