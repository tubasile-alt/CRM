"""create physical agenda import log

Revision ID: e2f3a4b5c6d7
Revises: d1e2f3a4b5c6
Create Date: 2026-07-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = 'e2f3a4b5c6d7'
down_revision = 'd1e2f3a4b5c6'
branch_labels = None
depends_on = None


def upgrade():
    if sa.inspect(op.get_bind()).has_table('physical_agenda_import_log'):
        return
    op.create_table(
        'physical_agenda_import_log',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('idempotency_key', sa.String(length=64), nullable=False),
        sa.Column('appointment_id', sa.Integer(), nullable=True),
        sa.Column('doctor_id', sa.Integer(), nullable=True),
        sa.Column('patient_id', sa.Integer(), nullable=True),
        sa.Column('performed_by_user_id', sa.Integer(), nullable=True),
        sa.Column('source_date', sa.Date(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['appointment_id'], ['appointment.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['doctor_id'], ['user.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['patient_id'], ['patient.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['performed_by_user_id'], ['user.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('appointment_id'),
    )
    op.create_index(
        op.f('ix_physical_agenda_import_log_doctor_id'),
        'physical_agenda_import_log',
        ['doctor_id'],
        unique=False,
    )
    op.create_index(
        op.f('ix_physical_agenda_import_log_idempotency_key'),
        'physical_agenda_import_log',
        ['idempotency_key'],
        unique=True,
    )
    op.create_index(
        op.f('ix_physical_agenda_import_log_patient_id'),
        'physical_agenda_import_log',
        ['patient_id'],
        unique=False,
    )


def downgrade():
    if not sa.inspect(op.get_bind()).has_table('physical_agenda_import_log'):
        return
    op.drop_index(op.f('ix_physical_agenda_import_log_patient_id'), table_name='physical_agenda_import_log')
    op.drop_index(op.f('ix_physical_agenda_import_log_idempotency_key'), table_name='physical_agenda_import_log')
    op.drop_index(op.f('ix_physical_agenda_import_log_doctor_id'), table_name='physical_agenda_import_log')
    op.drop_table('physical_agenda_import_log')
