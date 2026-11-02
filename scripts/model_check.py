"""Compare the optimized artefacts of two models on the same regions.

    python scripts/model_check.py

The study's optimized artefacts (``examples/``) were written by one model;
a second model wrote its own for one region per stratum, kept in
``results/raw/model_check/<region_id>/`` (record corpus/403). Both are
measured the way ``compare`` measures, and the three token reductions —
care (original → optimized.py), notation (optimized.py → optimized.ldpy),
total — are set side by side, on all tokens and on the host code.
Writes ``results/summary/model_check.json``.
"""

from __future__ import annotations

import json
import statistics
from pathlib import Path

from rdfeval.compare import NOT_SHIMS, ldpy_side, python_side, strip_demo

ROOT = Path(__file__).resolve().parent.parent
CHECK = ROOT / "results/raw/model_check"


def _steps(py: dict, opy: dict, old: dict) -> dict:
    def red(a, b, m):
        return round(100.0 * (a[m] - b[m]) / a[m], 2) if a[m] else None
    return {m: {"care": red(py, opy, m), "notation": red(opy, old, m),
                "total": red(py, old, m)}
            for m in ("tokens", "tokens_host")}


def main() -> dict:
    sample = json.loads((ROOT / "results/raw/optimize_sample.json").read_text())
    rows = []
    for stratum, regions in sample["strata"].items():
        for e in regions:
            if not e["model_check"]:
                continue
            ex = ROOT / e["dir"]
            other = CHECK / e["region_id"]
            shims = [p for p in sorted(ex.glob("*.py")) if p.name not in NOT_SHIMS]
            pre = "\n".join(p.read_text() for p in shims) or None
            py = python_side(strip_demo((ex / "original.py").read_text()), pre)

            def measure(d):
                return _steps(
                    py,
                    python_side(strip_demo((d / "optimized.py").read_text()), pre),
                    ldpy_side(strip_demo((d / "optimized.ldpy").read_text()), pre))
            rows.append({"region_id": e["region_id"], "stratum": stratum,
                         "study": measure(ex), "check": measure(other)})
    summary = {}
    for who in ("study", "check"):
        summary[who] = {
            m: {s: statistics.median(r[who][m][s] for r in rows
                                     if r[who][m][s] is not None)
                for s in ("care", "notation", "total")}
            for m in ("tokens", "tokens_host")}
    out = {"models": {"study": "Opus", "check": "Fable"},
           "n": len(rows), "median": summary, "regions": rows}
    (ROOT / "results/summary/model_check.json").write_text(
        json.dumps(out, indent=2, ensure_ascii=False) + "\n")
    return out


if __name__ == "__main__":
    r = main()
    print(json.dumps(r["median"], indent=1))
    for row in r["regions"]:
        a, b = row["study"]["tokens"], row["check"]["tokens"]
        print(f"{row['stratum']:24s} care {a['care']:+6.1f} {b['care']:+6.1f}"
              f"  notation {a['notation']:+6.1f} {b['notation']:+6.1f}"
              f"  total {a['total']:+6.1f} {b['total']:+6.1f}")
