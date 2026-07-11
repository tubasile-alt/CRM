from pathlib import Path
import subprocess
import sys

TEST_PATH = Path("tests/test_route_contract.py")
old_block = '''KNOWN_DUPLICATE_ROUTE_METHODS = {
    ("/api/patient/<int:patient_id>/surgeries", "GET"): [
        "get_patient_surgeries",
        "patient.get_patient_surgeries",
    ],
    ("/api/patient/<int:patient_id>/surgery", "POST"): [
        "create_patient_surgery",
        "patient.create_patient_surgery",
    ],
}
'''
new_block = "KNOWN_DUPLICATE_ROUTE_METHODS = {}\n"

test_source = TEST_PATH.read_text(encoding="utf-8")
if old_block in test_source:
    TEST_PATH.write_text(test_source.replace(old_block, new_block, 1), encoding="utf-8")
elif new_block not in test_source:
    raise SystemExit("Baseline conhecido de duplicidades não encontrado no formato esperado")

result = subprocess.run(
    [sys.executable, "scripts/audit_routes.py", "--output", "route-inventory.json"],
    text=True,
    capture_output=True,
)
output = (result.stdout or "") + (result.stderr or "")
print(output, end="")
if result.returncode:
    Path(".github/phase1_snapshot_error.txt").write_text(output, encoding="utf-8")
    raise SystemExit(result.returncode)
