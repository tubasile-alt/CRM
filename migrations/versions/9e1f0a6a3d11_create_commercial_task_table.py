"""create commercial task table

Revision ID: 9e1f0a6a3d11
Revises: 4fc309ae60d0
Create Date: 2026-03-12 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from werkzeug.security import generate_password_hash


# revision identifiers, used by Alembic.
revision = '9e1f0a6a3d11'
down_revision = '4fc309ae60d0'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'commercial_task',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('patient_id', sa.Integer(), nullable=False),
        sa.Column('patient_name_snapshot', sa.String(length=100), nullable=False),
        sa.Column('doctor_id', sa.Integer(), nullable=False),
        sa.Column('doctor_name_snapshot', sa.String(length=100), nullable=False),
        sa.Column('consultation_id', sa.Integer(), nullable=False),
        sa.Column('source_type', sa.String(length=20), nullable=False),
        sa.Column('planning_snapshot_json', sa.Text(), nullable=False),
        sa.Column('total_value', sa.Numeric(10, 2), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('priority', sa.String(length=20), nullable=False),
        sa.Column('seller_notes', sa.Text(), nullable=True),
        sa.Column('next_followup_date', sa.Date(), nullable=True),
        sa.Column('last_contact_at', sa.DateTime(), nullable=True),
        sa.Column('consultation_date', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['consultation_id'], ['appointment.id'], ),
        sa.ForeignKeyConstraint(['doctor_id'], ['user.id'], ),
        sa.ForeignKeyConstraint(['patient_id'], ['patient.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('consultation_id', 'source_type', name='uq_commercial_task_consultation_source')
    )

    op.create_index(op.f('ix_commercial_task_consultation_date'), 'commercial_task', ['consultation_date'], unique=False)
    op.create_index(op.f('ix_commercial_task_consultation_id'), 'commercial_task', ['consultation_id'], unique=False)
    op.create_index(op.f('ix_commercial_task_created_at'), 'commercial_task', ['created_at'], unique=False)
    op.create_index(op.f('ix_commercial_task_doctor_id'), 'commercial_task', ['doctor_id'], unique=False)
    op.create_index(op.f('ix_commercial_task_next_followup_date'), 'commercial_task', ['next_followup_date'], unique=False)
    op.create_index(op.f('ix_commercial_task_patient_id'), 'commercial_task', ['patient_id'], unique=False)
    op.create_index(op.f('ix_commercial_task_source_type'), 'commercial_task', ['source_type'], unique=False)
    op.create_index(op.f('ix_commercial_task_status'), 'commercial_task', ['status'], unique=False)

    user_table = sa.table(
        'user',
        sa.column('id', sa.Integer),
        sa.column('username', sa.String),
        sa.column('email', sa.String),
        sa.column('name', sa.String),
        sa.column('password_hash', sa.String),
        sa.column('role', sa.String),
        sa.column('role_clinico', sa.String),
    )
    conn = op.get_bind()
    existing = conn.execute(
        sa.select(user_table.c.id).where(
            sa.or_(
                user_table.c.username == 'marcella',
                user_table.c.email == 'marcella@clinicabasile.local'
            )
        )
    ).first()

    if existing:
        conn.execute(
            user_table.update()
            .where(user_table.c.id == existing.id)
            .values(
                name='Marcella',
                role='secretaria',
                role_clinico='SECRETARY',
                password_hash=generate_password_hash('654321')
            )
        )
    else:
        conn.execute(
            user_table.insert().values(
                username='marcella',
                email='marcella@clinicabasile.local',
                name='Marcella',
                role='secretaria',
                role_clinico='SECRETARY',
                password_hash=generate_password_hash('654321')
            )
        )


def downgrade():
    op.drop_index(op.f('ix_commercial_task_status'), table_name='commercial_task')
    op.drop_index(op.f('ix_commercial_task_source_type'), table_name='commercial_task')
    op.drop_index(op.f('ix_commercial_task_patient_id'), table_name='commercial_task')
    op.drop_index(op.f('ix_commercial_task_next_followup_date'), table_name='commercial_task')
    op.drop_index(op.f('ix_commercial_task_doctor_id'), table_name='commercial_task')
    op.drop_index(op.f('ix_commercial_task_created_at'), table_name='commercial_task')
    op.drop_index(op.f('ix_commercial_task_consultation_id'), table_name='commercial_task')
    op.drop_index(op.f('ix_commercial_task_consultation_date'), table_name='commercial_task')
    op.drop_table('commercial_task')
