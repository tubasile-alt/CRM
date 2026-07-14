"""Shared helpers extracted from app.py without behavior changes."""

from models import Appointment
from models import ProcedureExecution
from models import db


def build_patient_timeline(p_id):
    from collections import defaultdict
    from datetime import date, datetime
    from models import Evolution, CosmeticProcedurePlan, Surgery, TransplantSurgeryRecord
    events_by_day = defaultdict(list)

    def safe_parse_date(s):
        if not s:
            return None
        if isinstance(s, datetime):
            return s.date()
        if isinstance(s, date):
            return s
        try:
            return datetime.strptime(s, '%Y-%m-%d').date()
        except Exception:
            try:
                return datetime.fromisoformat(s.replace('Z', '')).date()
            except Exception:
                return None

    def to_dt(val, default_hour=12):
        if isinstance(val, datetime):
            return val
        if isinstance(val, date):
            return datetime.combine(val, datetime.min.time().replace(hour=default_hour))
        return None

    appts = Appointment.query.filter(
        Appointment.patient_id == p_id,
        Appointment.status != 'faltou'
    ).all()
    for apt in appts:
        raw = apt.consultation_date or apt.start_time
        if not raw:
            continue
        dt = to_dt(raw)
        d = dt.date()
        events_by_day[d].append({
            "type": "consulta",
            "dt": dt,
            "title": apt.timeline_label or f"Consulta: {apt.appointment_type or 'Geral'}",
            "label": apt.appointment_type or 'Consulta',
            "body": apt.notes or "",
            "id": apt.id,
            "appointment_id": apt.id,
            "reference_id": apt.id,
            "status": apt.status,
            "editable": True,
            "doctor": apt.doctor.name if apt.doctor else 'Médico'
        })

    from models import Note as _Note, CosmeticProcedurePlan as _CPP
    cosmetic_plans = _CPP.query.join(_Note).filter(
        _Note.patient_id == p_id,
        db.exists().where(ProcedureExecution.plan_id == _CPP.id).where(ProcedureExecution.execution_status == 'realizada')
    ).all()
    for plan in cosmetic_plans:
        d = safe_parse_date(plan.performed_date)
        if not d:
            if plan.note and plan.note.created_at:
                d = plan.note.created_at.date()
            else:
                continue
        dt = datetime.combine(d, datetime.min.time().replace(hour=12))
        events_by_day[d].append({
            "type": "procedimento",
            "dt": dt,
            "title": f"Procedimento: {plan.procedure_name}",
            "label": plan.procedure_name,
            "body": f"Realizado em {d.strftime('%d/%m/%Y')}. {getattr(plan, 'observations', '') or ''}",
            "id": plan.id,
            "reference_id": plan.id,
            "appointment_id": plan.note.appointment_id if plan.note else None,
            "doctor": plan.note.doctor.name if plan.note and plan.note.doctor else 'Médico'
        })

    surgeries = Surgery.query.filter_by(patient_id=p_id).all()
    for surg in surgeries:
        d = surg.date if isinstance(surg.date, date) else safe_parse_date(str(surg.date))
        if not d:
            continue
        start = getattr(surg, 'start_time', None)
        dt = datetime.combine(d, start) if start else datetime.combine(d, datetime.min.time().replace(hour=8))
        events_by_day[d].append({
            "type": "cirurgia",
            "dt": dt,
            "title": f"Cirurgia: {surg.procedure_name}",
            "label": surg.procedure_name,
            "body": surg.notes or "",
            "id": surg.id,
            "reference_id": surg.id,
            "status": getattr(surg, 'status', ''),
            "doctor": surg.doctor.name if surg.doctor else 'Médico'
        })

    ts_records = TransplantSurgeryRecord.query.filter_by(patient_id=p_id).all()
    for ts in ts_records:
        d = ts.surgery_date if isinstance(ts.surgery_date, date) else safe_parse_date(str(ts.surgery_date))
        if not d:
            continue
        dt = datetime.combine(d, datetime.min.time().replace(hour=8))
        events_by_day[d].append({
            "type": "cirurgia",
            "dt": dt,
            "title": f"Transplante Capilar: {ts.surgery_type or ''}",
            "label": "Transplante Capilar",
            "body": ts.observations or "",
            "id": ts.id,
            "reference_id": ts.id,
            "doctor": ts.doctor.name if ts.doctor else 'Médico'
        })

    evos = Evolution.query.filter_by(patient_id=p_id).all()
    for evo in evos:
        raw = getattr(evo, 'evolution_date', None) or evo.created_at
        if not raw:
            continue
        dt = to_dt(raw)
        if not dt:
            continue
        d = dt.date()
        events_by_day[d].append({
            "type": "evolution",
            "dt": dt,
            "title": "Evolução clínica",
            "label": "Evolução",
            "body": evo.content or "(Sem conteúdo)",
            "id": evo.id,
            "reference_id": evo.id,
            "doctor": evo.doctor.name if evo.doctor else 'Médico'
        })

    type_order = {"cirurgia": 0, "procedimento": 1, "consulta": 2, "evolution": 3}
    timeline = []
    for d in sorted(events_by_day.keys()):
        day_events = sorted(
            events_by_day[d],
            key=lambda x: (type_order.get(x["type"], 99), x["dt"])
        )
        timeline.append({
            "date": d.strftime('%Y-%m-%d'),
            "label": d.strftime('%d/%m/%Y'),
            "dt": day_events[0]["dt"],
            "type": day_events[0]["type"],
            "events": day_events
        })
    return timeline
