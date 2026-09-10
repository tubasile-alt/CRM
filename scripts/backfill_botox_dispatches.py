"""Cria dispatches históricos de Botox sem enviar mensagens."""

from __future__ import annotations

import argparse
import os
import sys
from collections import Counter
from datetime import timedelta
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

os.environ.setdefault('DISABLE_SCHEDULER', '1')

from app import app  # noqa: E402
from models import (  # noqa: E402
    CosmeticProcedurePlan,
    MessageDispatch,
    Note,
    ProcedureExecution,
    db,
)
from services.clinic_time import clinic_today  # noqa: E402
from services.followup_service import (  # noqa: E402
    build_dispatch_rows,
    is_botox,
)


def _build_backfill_rows(today):
    executions = db.session.query(ProcedureExecution).join(
        CosmeticProcedurePlan,
        ProcedureExecution.plan_id == CosmeticProcedurePlan.id,
    ).join(
        Note,
        CosmeticProcedurePlan.note_id == Note.id,
    ).filter(
        ProcedureExecution.execution_status == 'realizada',
        ProcedureExecution.performed_date.isnot(None),
    ).order_by(ProcedureExecution.performed_date.asc()).all()

    existing = {
        (patient_id, message_type, due_at)
        for patient_id, message_type, due_at in db.session.query(
            MessageDispatch.patient_id,
            MessageDispatch.message_type,
            MessageDispatch.due_at,
        ).all()
    }

    output = []
    processed = 0
    suppressed = 0
    for execution in executions:
        plan = execution.plan
        if not is_botox(plan.procedure_name):
            continue
        processed += 1
        patient_id = plan.note.patient_id
        for row in build_dispatch_rows(execution, plan, today=today):
            key = (patient_id, row['message_type'], row['due_at'])
            if key in existing:
                suppressed += 1
                continue
            row = dict(row)
            row['patient_id'] = patient_id
            if row['message_type'] == 'd0':
                row['status'] = 'pulada'
            elif row['due_at'] < today - timedelta(days=30):
                row['status'] = 'pulada'
            else:
                row['status'] = 'pendente'
            output.append(row)
            existing.add(key)
    return output, processed, suppressed


def _print_summary(rows, processed, suppressed, today):
    counts = Counter((row['message_type'], row['status']) for row in rows)
    upcoming = sum(
        1
        for row in rows
        if row['message_type'] == 'm5'
        and row['status'] == 'pendente'
        and today <= row['due_at'] <= today + timedelta(days=30)
    )
    print(f"d0  pulada   : {counts[('d0', 'pulada')]}")
    print(f"m5  pulada   : {counts[('m5', 'pulada')]}")
    print(
        f"m5  pendente : {counts[('m5', 'pendente')]} "
        f"(destes, {upcoming} vencem nos próximos 30 dias)"
    )
    print(f"dispatches após dedupe      : {len(rows)}")
    print(f"duplicatas suprimidas       : {suppressed}")
    print(f"total execuções botox realizadas processadas: {processed}")


def main():
    parser = argparse.ArgumentParser(
        description='Backfill de dispatches D0 e M5 para Botox.',
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        '--dry-run',
        action='store_true',
        help='Calcula e exibe o resultado sem gravar (padrão).',
    )
    mode.add_argument(
        '--commit',
        action='store_true',
        help='Grava os dispatches ausentes.',
    )
    args = parser.parse_args()

    with app.app_context():
        today = clinic_today()
        rows, processed, suppressed = _build_backfill_rows(today)
        _print_summary(rows, processed, suppressed, today)
        if not args.commit:
            print('dry-run: nenhuma alteração gravada')
            return 0

        if rows:
            db.session.execute(MessageDispatch.__table__.insert(), rows)
        db.session.commit()
        print(f'commit: {len(rows)} dispatches gravados')
        return 0


if __name__ == '__main__':
    raise SystemExit(main())