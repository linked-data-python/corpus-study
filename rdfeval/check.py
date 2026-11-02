"""Check one translated pair: does it transpile, and does its driver agree?

    python -m rdfeval check examples/<stratum>/<region_id>

The two machine checks of the protocol, in one command and in order:

  1. ``translated.ldpy`` transpiles (the island syntax is valid);
  2. the driver runs and prints ``equivalent: true``.

A region that also carries the optimized artefacts of design record
``corpus/403`` (``optimized.py``, ``optimized.ldpy``) gets the same two
checks for each of them, with the same driver, against ``original.py``
(``RDFEVAL_SIDES``, see :mod:`rdfeval.harness`).

Both are PRE-conditions to human review — a pair that fails either does not
reach a reviewer.  Exit code 0 only when every artefact passes, so a batch
can be driven from a shell loop.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from .harness import DEFAULT_SIDES, SIDES_ENV

OPTIMIZED = ("optimized.py", "optimized.ldpy")
#: The header variant: the optimized artefacts with the extracted header
#: optimized too (AGENT_OPTIMIZE.md, "The header variant").
HEADER = ("optimized_header.py", "optimized_header.ldpy")


def _compiles(path: Path) -> str | None:
    """None if the artefact is valid syntax, else the reason."""
    try:
        if path.suffix == ".ldpy":
            from ldpy.transpiler import transpile
            transpile(path.read_text(), filename=str(path))
        else:
            compile(path.read_text(), str(path), "exec")
    except Exception as e:                        # noqa: BLE001 - reported
        verb = "transpile" if path.suffix == ".ldpy" else "compile"
        return f"{verb}: {type(e).__name__}: {e}"
    return None


def check(ex_dir: Path, timeout: int = 120,
          sides: tuple[str, str] = DEFAULT_SIDES) -> dict:
    ex_dir = ex_dir.resolve()
    right = sides[1]
    out: dict = {"example": ex_dir.name, "artefact": right,
                 "transpiles": False, "verdict": None, "ok": False,
                 "error": None}
    target = ex_dir / right
    if not target.exists():
        out["error"] = f"no {right} in {ex_dir}"
        return out
    error = _compiles(target)
    if error:
        out["error"] = error
        return out
    out["transpiles"] = True

    driver = ex_dir / "driver.py"
    if not driver.exists():
        out["error"] = "no driver.py"
        return out
    env = {**os.environ, SIDES_ENV: ",".join(sides)}
    try:
        proc = subprocess.run([sys.executable, driver.name], cwd=ex_dir,
                              capture_output=True, text=True, timeout=timeout,
                              env=env)
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
    if out["verdict"].get("sides", list(DEFAULT_SIDES)) != list(sides):
        # a driver that bypasses run_pair would prove the default pair again
        out["error"] = (f"driver compared {out['verdict'].get('sides')}, "
                        f"not {list(sides)}")
        return out
    out["ok"] = bool(out["verdict"].get("equivalent"))
    if not out["ok"]:
        out["error"] = (out["verdict"].get("error")
                        or "; ".join(out["verdict"].get("diffs", [])))
    return out


def check_region(ex_dir: Path, timeout: int = 120) -> list[dict]:
    """The translated pair, then every optimized artefact present."""
    results = [check(ex_dir, timeout)]
    for name in OPTIMIZED + HEADER:
        if (Path(ex_dir) / name).exists():
            results.append(check(ex_dir, timeout, ("original.py", name)))
    return results


def sizes(ex_dir: Path) -> str | None:
    """Token ratios of the optimized artefacts, for the translator's eye."""
    ex_dir = Path(ex_dir)
    if not all((ex_dir / n).exists() for n in OPTIMIZED):
        return None
    from .compare import (NOT_SHIMS, measure_optimized, python_side,
                          strip_demo)
    shims = [p for p in sorted(ex_dir.glob("*.py")) if p.name not in NOT_SHIMS]
    preamble = "\n".join(p.read_text() for p in shims) or None
    try:
        # measured as compare measures it: without the demo() harness, which
        # measure_optimized strips from the optimized artefacts too
        py = python_side(strip_demo((ex_dir / "original.py").read_text()),
                         preamble)
        opt = measure_optimized(py, (ex_dir / "optimized.py").read_text(),
                                (ex_dir / "optimized.ldpy").read_text(),
                                preamble)
    except Exception as e:                        # noqa: BLE001 - reported
        return f"sizes: {type(e).__name__}: {e}"
    r = {k: opt[f"ratios_{k}"]["tokens"] for k in ("care", "notation", "total")}
    line = (f"tokens: care {r['care']} (original → optimized.py), "
            f"notation {r['notation']} (optimized.py → optimized.ldpy), "
            f"total {r['total']}")
    if all((ex_dir / n).exists() for n in HEADER):
        h = measure_optimized(py, (ex_dir / HEADER[0]).read_text(),
                              (ex_dir / HEADER[1]).read_text(), preamble)
        r = {k: h[f"ratios_{k}"]["tokens"] for k in ("care", "notation", "total")}
        line += (f"\n     header variant: care {r['care']} notation "
                 f"{r['notation']} total {r['total']}")
    return line


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if not args:
        print(__doc__)
        return 2
    failures = 0
    for target in args:
        d = Path(target)
        for result in check_region(d):
            mark = "OK  " if result["ok"] else "FAIL"
            print(f"{mark} {d} [{result['artefact']}]")
            if not result["ok"]:
                failures += 1
                print(f"     {result['error']}")
            elif result["verdict"].get("method"):
                print(f"     method: {result['verdict']['method']}")
        line = sizes(d)
        if line:
            print(f"     {line}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
