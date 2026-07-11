from __future__ import annotations

import ast
import builtins
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
APP_PATH = ROOT / "app.py"

GROUPS = {
    "services/patient_identity.py": [
        "generate_next_patient_code",
        "normalize_patient_name",
        "find_possible_duplicate_patients",
    ],
    "services/execution_service.py": [
        "_parse_date_or_datetime",
        "_serialize_execution",
        "_build_execution_from_payload",
    ],
    "services/finalization_service.py": [
        "_note_counts_as_finalized",
        "_find_finalized_note",
        "_resolve_consultation_finalization",
    ],
    "services/timeline_service.py": ["build_patient_timeline"],
    "services/doctor_service.py": ["get_doctor_id", "get_all_doctors"],
}

CLINIC_TIME_FUNCTIONS = [
    "get_brazil_time",
    "parse_datetime_with_tz",
    "format_brazil_datetime",
]

KEEP_IN_APP = {
    "_ensure_patient_doctor_partial_index",
    "_ensure_physical_agenda_import_log_schema",
    "_ensure_index_on_startup",
    "_activation_warnings_for",
    "_activation_required_errors",
    "_audit_access_required",
    "_run_in_app_context",
    "start_smart_no_show_scheduler",
}

IMPORT_MAP = {
    "db": "from models import db",
    "Patient": "from models import Patient",
    "PatientDoctor": "from models import PatientDoctor",
    "ProcedureExecution": "from models import ProcedureExecution",
    "User": "from models import User",
    "datetime": "from datetime import datetime",
    "date": "from datetime import date",
    "timedelta": "from datetime import timedelta",
    "pytz": "import pytz",
    "clinic_now": "from services.clinic_time import clinic_now",
    "clinic_today": "from services.clinic_time import clinic_today",
    "get_brazil_time": "from services.clinic_time import get_brazil_time",
}

BUILTINS = set(dir(builtins)) | {"None", "True", "False"}


def top_level_functions(tree: ast.Module) -> dict[str, ast.FunctionDef | ast.AsyncFunctionDef]:
    return {
        node.name: node
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }


def source_segment(lines: list[str], node: ast.AST) -> str:
    assert hasattr(node, "lineno") and hasattr(node, "end_lineno")
    return "".join(lines[node.lineno - 1 : node.end_lineno]).rstrip() + "\n"


def local_names(node: ast.AST) -> set[str]:
    names: set[str] = set()
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        for arg in (*node.args.posonlyargs, *node.args.args, *node.args.kwonlyargs):
            names.add(arg.arg)
        if node.args.vararg:
            names.add(node.args.vararg.arg)
        if node.args.kwarg:
            names.add(node.args.kwarg.arg)
    for child in ast.walk(node):
        if isinstance(child, ast.Name) and isinstance(child.ctx, (ast.Store, ast.Del)):
            names.add(child.id)
        elif isinstance(child, ast.Import):
            for alias in child.names:
                names.add(alias.asname or alias.name.split(".")[0])
        elif isinstance(child, ast.ImportFrom):
            for alias in child.names:
                names.add(alias.asname or alias.name)
    return names


def loaded_names(nodes: list[ast.AST]) -> set[str]:
    return {
        child.id
        for node in nodes
        for child in ast.walk(node)
        if isinstance(child, ast.Name) and isinstance(child.ctx, ast.Load)
    }


def imports_for(nodes: list[ast.AST], sibling_names: set[str], extra_locals: set[str] | None = None) -> list[str]:
    locals_seen = set(extra_locals or set()) | sibling_names
    for node in nodes:
        locals_seen |= local_names(node)
    external = loaded_names(nodes) - locals_seen - BUILTINS
    unknown = sorted(name for name in external if name not in IMPORT_MAP)
    if unknown:
        raise RuntimeError(
            "Dependências globais não mapeadas ao extrair helpers: " + ", ".join(unknown)
        )
    return sorted({IMPORT_MAP[name] for name in external})


def remove_ranges(lines: list[str], ranges: list[tuple[int, int]]) -> list[str]:
    remove = set()
    for start, end in ranges:
        remove.update(range(start - 1, end))
    output = [line for index, line in enumerate(lines) if index not in remove]
    text = "".join(output)
    text = re.sub(r"\n{4,}", "\n\n\n", text)
    return text.splitlines(keepends=True)


def write_service(path: str, nodes: list[ast.AST], segments: list[str], extra_locals: set[str] | None = None) -> None:
    imports = imports_for(nodes, {getattr(node, "name") for node in nodes}, extra_locals)
    content = '"""Shared helpers extracted from app.py without behavior changes."""\n\n'
    if imports:
        content += "\n".join(imports) + "\n\n\n"
    content += "\n\n".join(segment.rstrip() for segment in segments) + "\n"
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


def update_clinic_time(segments: list[str], nodes: list[ast.AST]) -> None:
    path = ROOT / "services/clinic_time.py"
    content = path.read_text(encoding="utf-8")
    required = imports_for(nodes, set(CLINIC_TIME_FUNCTIONS))
    lines = content.splitlines(keepends=True)
    existing = {line.strip() for line in lines}
    missing = [statement for statement in required if statement not in existing]
    if missing:
        insert_at = 1 if lines and lines[0].lstrip().startswith(('"""', "'''")) else 0
        # Preserve existing module structure; add only genuinely required imports.
        lines[insert_at:insert_at] = [statement + "\n" for statement in missing] + ["\n"]
        content = "".join(lines)
    if not content.endswith("\n"):
        content += "\n"
    content += "\n\n" + "\n\n".join(segment.rstrip() for segment in segments) + "\n"
    path.write_text(content, encoding="utf-8")


def replace_imports(app_text: str) -> str:
    clinic_pattern = re.compile(r"^from services\.clinic_time import .*$", re.MULTILINE)
    clinic_line = (
        "from services.clinic_time import clinic_now, clinic_today, clinic_wall_time_iso, "
        "utc_instant_to_clinic_iso, get_brazil_time, parse_datetime_with_tz, "
        "format_brazil_datetime"
    )
    if not clinic_pattern.search(app_text):
        raise RuntimeError("Import existente de services.clinic_time não encontrado")
    app_text = clinic_pattern.sub(clinic_line, app_text, count=1)
    new_imports = [
        "from services.patient_identity import NEW_PATIENT_CODE_START, generate_next_patient_code, normalize_patient_name, find_possible_duplicate_patients",
        "from services.execution_service import _parse_date_or_datetime, _serialize_execution, _build_execution_from_payload",
        "from services.finalization_service import _note_counts_as_finalized, _find_finalized_note, _resolve_consultation_finalization",
        "from services.timeline_service import build_patient_timeline",
        "from services.doctor_service import get_doctor_id, get_all_doctors",
    ]
    anchor = clinic_line + "\n"
    return app_text.replace(anchor, anchor + "\n".join(new_imports) + "\n", 1)


def main() -> None:
    source = APP_PATH.read_text(encoding="utf-8")
    lines = source.splitlines(keepends=True)
    tree = ast.parse(source)
    functions = top_level_functions(tree)

    requested = set(CLINIC_TIME_FUNCTIONS)
    for names in GROUPS.values():
        requested.update(names)

    missing = sorted(requested - set(functions))
    if missing:
        # A second workflow run after the refactor should be a harmless no-op.
        if all(f"from services." in source for _ in [0]) and "def get_brazil_time" not in source:
            print("Helpers já extraídos; nenhuma alteração necessária.")
            return
        raise RuntimeError("Funções não encontradas por nome: " + ", ".join(missing))

    if not KEEP_IN_APP.issubset(functions):
        absent = sorted(KEEP_IN_APP - set(functions))
        raise RuntimeError("Funções que deveriam permanecer no app.py não encontradas: " + ", ".join(absent))

    constant_node = next(
        (
            node
            for node in tree.body
            if isinstance(node, ast.Assign)
            and any(isinstance(target, ast.Name) and target.id == "NEW_PATIENT_CODE_START" for target in node.targets)
        ),
        None,
    )
    if constant_node is None:
        raise RuntimeError("NEW_PATIENT_CODE_START não encontrada")

    patient_nodes = [functions[name] for name in GROUPS["services/patient_identity.py"]]
    patient_segments = ["NEW_PATIENT_CODE_START = 1001\n"] + [source_segment(lines, node) for node in patient_nodes]
    write_service(
        "services/patient_identity.py",
        patient_nodes,
        patient_segments,
        extra_locals={"NEW_PATIENT_CODE_START"},
    )

    for path, names in GROUPS.items():
        if path == "services/patient_identity.py":
            continue
        nodes = [functions[name] for name in names]
        write_service(path, nodes, [source_segment(lines, node) for node in nodes])

    clinic_nodes = [functions[name] for name in CLINIC_TIME_FUNCTIONS]
    update_clinic_time([source_segment(lines, node) for node in clinic_nodes], clinic_nodes)

    ranges = [(constant_node.lineno, constant_node.end_lineno)]
    ranges.extend((functions[name].lineno, functions[name].end_lineno) for name in requested)
    new_lines = remove_ranges(lines, ranges)
    new_source = replace_imports("".join(new_lines))
    APP_PATH.write_text(new_source, encoding="utf-8")

    # Safety checks requested for this phase.
    final_tree = ast.parse(new_source)
    final_functions = top_level_functions(final_tree)
    duplicated = sorted(requested & set(final_functions))
    if duplicated:
        raise RuntimeError("Definições ainda presentes no app.py: " + ", ".join(duplicated))
    if not KEEP_IN_APP.issubset(final_functions):
        raise RuntimeError("Uma função de startup/scheduler proibida foi removida")

    for path in GROUPS:
        service_text = (ROOT / path).read_text(encoding="utf-8")
        if "from app import" in service_text:
            raise RuntimeError(f"Import circular detectado em {path}")

    print("Extração da Fase 1 concluída sem renames e sem mover rotas.")


if __name__ == "__main__":
    main()
