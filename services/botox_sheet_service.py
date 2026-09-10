"""Reconciliação da aba Botox do Google Sheets a partir do banco.

A planilha é um espelho de leitura: reconstruída por completo a cada execução.
Nenhum caminho de request escreve nela.
"""

from collections import OrderedDict

from sqlalchemy import text


ADVISORY_LOCK_KEY = 918273


def build_botox_sheet_rows():
    """Retorna a matriz de valores, agrupada por paciente e data."""
    from models import CosmeticProcedurePlan, Note, Patient, ProcedureExecution, db
    from services.google_sheets import BOTOX_HEADERS, format_phone_for_sheets

    rows = (
        db.session.query(ProcedureExecution, Patient)
        .join(
            CosmeticProcedurePlan,
            ProcedureExecution.plan_id == CosmeticProcedurePlan.id,
        )
        .join(Note, CosmeticProcedurePlan.note_id == Note.id)
        .join(Patient, Note.patient_id == Patient.id)
        .filter(
            ProcedureExecution.execution_status == 'realizada',
            ProcedureExecution.performed_date.isnot(None),
            db.func.lower(CosmeticProcedurePlan.procedure_name).like('%botox%'),
        )
        .order_by(
            ProcedureExecution.performed_date.asc(),
            ProcedureExecution.id.asc(),
        )
        .all()
    )

    groups = OrderedDict()
    for execution, patient in rows:
        key = (patient.id, execution.performed_date.date())
        group = groups.setdefault(key, {
            'patient': patient,
            'performed_date': execution.performed_date,
            'followup_date': execution.followup_date,
            'execution_ids': [],
        })
        group['execution_ids'].append(execution.id)
        if not group['followup_date'] and execution.followup_date:
            group['followup_date'] = execution.followup_date

    from models import MessageDispatch

    patient_ids = [group['patient'].id for group in groups.values()]
    dispatches = []
    if patient_ids:
        dispatches = db.session.query(MessageDispatch).filter(
            MessageDispatch.patient_id.in_(patient_ids)
        ).all()
    dispatch_by_key = {
        (dispatch.patient_id, dispatch.message_type, dispatch.due_at): dispatch
        for dispatch in dispatches
    }

    def _d(value):
        return value.strftime('%d/%m/%Y') if value else ''

    def _dt(value):
        return value.strftime('%d/%m/%Y %H:%M') if value else ''

    matrix = [list(BOTOX_HEADERS)]
    for group in groups.values():
        patient = group['patient']
        performed_date = group['performed_date']
        followup_date = group['followup_date']
        disp_d0 = dispatch_by_key.get(
            (patient.id, 'd0', performed_date.date())
        )
        disp_m5 = dispatch_by_key.get(
            (
                patient.id,
                'm5',
                followup_date.date() if followup_date else None,
            )
        )
        matrix.append([
            ', '.join(str(execution_id) for execution_id in group['execution_ids']),
            patient.name or '',
            format_phone_for_sheets(patient.phone),
            _d(performed_date),
            _d(followup_date),
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