from pathlib import Path
import subprocess
import sys

result = subprocess.run(
    [sys.executable, "-m", "tests.generate_url_snapshot"],
    text=True,
    capture_output=True,
)
output = (result.stdout or "") + (result.stderr or "")
if result.returncode:
    inventory = subprocess.run(
        ["bash", "-lc", "find tests -maxdepth 3 -type f -print | sort"],
        text=True,
        capture_output=True,
    )
    output += "\n\nFILES_IN_TESTS:\n" + (inventory.stdout or inventory.stderr or "")
print(output, end="")
if result.returncode:
    Path(".github/phase1_snapshot_error.txt").write_text(output, encoding="utf-8")
    raise SystemExit(result.returncode)
