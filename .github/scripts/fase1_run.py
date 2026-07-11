from pathlib import Path
import traceback

from fase1_extract_services import IMPORT_MAP, main

# Candidate mappings are only emitted when the extracted AST actually loads the name.
# This keeps every service import limited to dependencies used by its copied bodies.
IMPORT_MAP.update({
    "current_user": "from flask_login import current_user",
    "jsonify": "from flask import jsonify",
    "request": "from flask import request",
    "abort": "from flask import abort",
    "Appointment": "from models import Appointment",
    "Note": "from models import Note",
    "Procedure": "from models import Procedure",
    "Indication": "from models import Indication",
    "CosmeticProcedurePlan": "from models import CosmeticProcedurePlan",
    "HairTransplant": "from models import HairTransplant",
    "Evolution": "from models import Evolution",
    "Surgery": "from models import Surgery",
    "PatientActivationLog": "from models import PatientActivationLog",
    "clinic_wall_time_iso": "from services.clinic_time import clinic_wall_time_iso",
    "utc_instant_to_clinic_iso": "from services.clinic_time import utc_instant_to_clinic_iso",
    "json": "import json",
    "re": "import re",
    "os": "import os",
})

try:
    main()
except Exception:
    diagnostic = traceback.format_exc()
    Path(".github/phase1_dependency_error.txt").write_text(diagnostic, encoding="utf-8")
    print(diagnostic)
    raise
