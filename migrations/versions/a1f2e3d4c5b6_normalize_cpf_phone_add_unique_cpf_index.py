"""normalize cpf/phone and add partial unique index on patient.cpf

Normaliza CPF e telefone legados para apenas dígitos e cria o índice único
parcial uq_patient_cpf (ignora NULL). Telefone NÃO recebe unicidade —
familiares compartilham número.

ATENÇÃO (deploy): se existirem CPFs duplicados na base, esta migration FALHA
de propósito listando os IDs conflitantes. Resolva os duplicados (merge ou
correção de CPF) antes de reexecutar. Query de auditoria:

    SELECT cpf, array_agg(id) FROM patient
    WHERE cpf IS NOT NULL GROUP BY cpf HAVING count(*) > 1;

O downgrade remove apenas o índice; a normalização de dados NÃO é revertida
(os valores originais mascarados não são preservados).

Revision ID: a1f2e3d4c5b6
Revises: e2f3a4b5c6d7
Create Date: 2026-07-07 00:00:00.000000

"""
import re

from alembic import op
import sqlalchemy as sa


revision = 'a1f2e3d4c5b6'
down_revision = 'e2f3a4b5c6d7'
branch_labels = None
depends_on = None


def _normalize_digits(value):
    if value is None:
        return None
    digits = re.sub(r'\D', '', str(value))
    return digits or None


def _normalize_legacy_rows(bind):
    """Reduz cpf/phone legados a dígitos (NULL quando vazio)."""
    if bind.dialect.name == 'postgresql':
        bind.execute(sa.text(
            "UPDATE patient SET "
            "cpf = NULLIF(regexp_replace(cpf, '\\D', '', 'g'), ''), "
            "phone = NULLIF(regexp_replace(phone, '\\D', '', 'g'), '')"
        ))
        return

    # SQLite (dev) não tem regexp_replace: normalizar em Python.
    rows = bind.execute(
        sa.text('SELECT id, cpf, phone FROM patient')
    ).fetchall()
    for row in rows:
        new_cpf = _normalize_digits(row.cpf)
        new_phone = _normalize_digits(row.phone)
        if new_cpf != row.cpf or new_phone != row.phone:
            bind.execute(
                sa.text('UPDATE patient SET cpf = :cpf, phone = :phone WHERE id = :id'),
                {'cpf': new_cpf, 'phone': new_phone, 'id': row.id},
            )


def _fail_if_duplicate_cpfs(bind):
    duplicates = bind.execute(sa.text(
        'SELECT cpf FROM patient WHERE cpf IS NOT NULL '
        'GROUP BY cpf HAVING count(*) > 1'
    )).fetchall()
    if not duplicates:
        return

    lines = []
    for (cpf,) in duplicates:
        ids = bind.execute(
            sa.text('SELECT id FROM patient WHERE cpf = :cpf ORDER BY id'),
            {'cpf': cpf},
        ).fetchall()
        lines.append(f"  CPF {cpf}: pacientes ids={[r.id for r in ids]}")

    raise RuntimeError(
        'Migration abortada: existem pacientes com CPF duplicado e o índice '
        'único uq_patient_cpf não pode ser criado.\n'
        + '\n'.join(lines)
        + '\nResolva os conflitos (merge de cadastros ou correção do CPF) via '
        'ferramenta de auditoria e reexecute a migration.'
    )


def upgrade():
    bind = op.get_bind()

    _normalize_legacy_rows(bind)
    _fail_if_duplicate_cpfs(bind)

    existing = {
        idx['name'] for idx in sa.inspect(bind).get_indexes('patient')
    }
    if 'uq_patient_cpf' not in existing:
        op.create_index(
            'uq_patient_cpf',
            'patient',
            ['cpf'],
            unique=True,
            postgresql_where=sa.text('cpf IS NOT NULL'),
            sqlite_where=sa.text('cpf IS NOT NULL'),
        )


def downgrade():
    # Remove apenas o índice. A normalização de cpf/phone NÃO é revertida:
    # os formatos mascarados originais não são preservados em lugar nenhum.
    bind = op.get_bind()
    existing = {
        idx['name'] for idx in sa.inspect(bind).get_indexes('patient')
    }
    if 'uq_patient_cpf' in existing:
        op.drop_index('uq_patient_cpf', table_name='patient')
