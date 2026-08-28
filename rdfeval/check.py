"""Check one translated pair: does it transpile, and does its driver agree?

    python -m rdfeval check examples403/<stratum>/<region_id>

The two machine checks of the 403 protocol, in one command and in order:

  1. ``translated.ldpy`` transpiles (the island syntax is valid);
  2. the driver runs and prints ``equivalent: true``.

Both are PRE-conditions to human review — a pair that fails either does not
reach a reviewer.  Exit code 0 only when both pass, so a batch can be driven
from a shell loop.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def check(ex_dir: Path, timeout: int = 120) -> dict:
    ex_dir = ex_dir.resolve()
    out: dict = {"example": ex_dir.name, "transpiles": False,
                 "verdict": None, "ok": False, "error": None}
    ldpy_file = ex_dir / "translated.ldpy"
    if not ldpy_file.exists():
        out["error"] = f"no translated.ldpy in {ex_dir}"
        return out
    try:
        from ldpy.transpiler import transpile
        transpile(ldpy_file.read_text(), filename=str(ldpy_file))
        out["transpiles"] = True
    except Exception as e:                        # noqa: BLE001 - reported
        out["error"] = f"transpile: {type(e).__name__}: {e}"
        return out

    driver = ex_dir / "driver.py"
    if not driver.exists():
        out["error"] = "no driver.py"
        return out
    try:
        proc = subprocess.run([sys.executable, driver.name], cwd=ex_dir,
                              capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        out["error"] = f"driver timeout ({timeout}s)"
        return out
    for line in proc.stderr.splitlines():
        if line.startswith("RDFEVAL-VERDICT "):
            out["verdict"] = json.loads(line[len("RDFEVAL-VERDICT "):])
            break
    if out["verdict"] is None:
        tail = (proc.stderr.strip() or proc.stdout.strip())[-1200:]
        out["error"] = f"driver produced no verdict (rc={proc.returncode}):\n{tail}"
        return out
    out["ok"] = bool(out["verdict"].get("equivalent"))
    if not out["ok"]:
        out["error"] = (out["verdict"].get("error")
                        or "; ".join(out["verdict"].get("diffs", [])))
    return out


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if not args:
        print(__doc__)
        return 2
    failures = 0
    for target in args:
        d = Path(target)
        result = check(d)
        mark = "OK  " if result["ok"] else "FAIL"
        print(f"{mark} {d}")
        if not result["ok"]:
            failures += 1
            print(f"     {result['error']}")
        elif result["verdict"].get("method"):
            print(f"     method: {result['verdict']['method']}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
