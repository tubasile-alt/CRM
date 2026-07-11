from pathlib import Path
import subprocess
import sys

result = subprocess.run(
    [sys.executable, "-m", "tests.generate_url_snapshot"],
    text=True,
    capture_output=True,
)
output = (result.stdout or "") + (result.stderr or "")
print(output, end="")
if result.returncode:
    Path(".github/phase1_snapshot_error.txt").write_text(output, encoding="utf-8")
    raise SystemExit(result.returncode)
