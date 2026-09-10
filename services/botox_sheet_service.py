"""Reconciliação da aba Botox do Google Sheets a partir do banco.

A planilha é um espelho de leitura: reconstruída por completo a cada execução.
Nenhum caminho de request escreve nela.
"""

from sqlalchemy import text
from sqlalchemy.orm import aliased


ADVISORY_LOCK_KEY = 918273


def build_botox_sheet_rows():
    """Retorna a matriz de valores da aba, cabeçalho incluído."""
    from models import (
        CosmeticProcedurePlan,
        MessageDispatch,
        Note,
        Patient,
        ProcedureExecution,
        db,
    )
    from services.google_sheets import BOTOX_HEADERS, format_phone_for_sheets

    d0 = aliased(MessageDispatch)
    m5 = aliased(MessageDispatch)

    rows = (
        db.session.query(ProcedureExecution, Patient, d0, m5)
        .join(
            CosmeticProcedurePlan,
            ProcedureExecution.plan_id == CosmeticProcedurePlan.id,
        )
        .join(Note, CosmeticProcedurePlan.note_id == Note.id)
        .join(Patient, Note.patient_id == Patient.id)
        .outerjoin(
            d0,
            db.and_(
                d0.execution_id == ProcedureExecution.id,
                d0.message_type == 'd0',
            ),
        )
        .outerjoin(
            m5,
            db.and_(
                m5.execution_id == ProcedureExecution.id,
                m5.message_type == 'm5',
            ),
        )
        .filter(
            ProcedureExecution.execution_status == 'realizada',
            ProcedureExecution.performed_date.isnot(None),
            db.func.lower(CosmeticProcedurePlan.procedure_name).like('%botox%'),
        )
        .order_by(ProcedureExecution.performed_date.asc())
        .all()
    )

    def _d(value):
        return value.strftime('%d/%m/%Y') if value else ''

    def _dt(value):
        return value.strftime('%d/%m/%Y %H:%M') if value else ''

    matrix = [list(BOTOX_HEADERS)]
    for execution, patient, disp_d0, disp_m5 in rows:
        matrix.append([
            execution.id,
            patient.name or '',
            format_phone_for_sheets(patient.phone),
            _d(execution.performed_date),
            _d(execution.followup_date),
            disp_d0.status if disp_d0 else '',
            _dt(disp_d0.sent_at) if disp_d0 else '',
            disp_m5.status if disp_m5 else '',
            _dt(disp_m5.sent_at) if disp_m5 else '',
        ])
    return matrix


def run_botox_sheet_sync():
    """Reconcilia a planilha, evitando concorrência entre workers."""
    from models import db
    from services.google_sheets import write_botox_sheet

    if db.engine.dialect.name != 'postgresql':
        return write_botox_sheet(build_botox_sheet_rows())

    with db.engine.connect() as connection:
        acquired = connection.execute(
            text('SELECT pg_try_advisory_lock(:key)'),
            {'key': ADVISORY_LOCK_KEY},
        ).scalar()
        if not acquired:
            return True, 'ignorado: outro worker já está sincronizando'

        try:
            return write_botox_sheet(build_botox_sheet_rows())
        finally:
            connection.execute(
                text('SELECT pg_advisory_unlock(:key)'),
                {'key': ADVISORY_LOCK_KEY},
            )