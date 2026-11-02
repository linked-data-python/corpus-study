"""What is left to optimize, in batches (record corpus/403).

    python scripts/plan_optimize.py [--batch-size 10]

Every proved pair of the resumed sample (record corpus/404) gets the
optimized artefacts and the header variant (AGENT_OPTIMIZE.md). The plan
is recomputed from ``meta.json`` each time, so a campaign interrupted by a
quota resumes where it stopped: a region is left out once its two
statuses are final, or once its optimization is a ``draft`` with a note
(a driver that cannot prove an artefact). Regions that already have final
optimized artefacts only need the header variant.

Writes ``results/summary/optimize_plan.json``: batches of region
directories, each tagged ``full`` (both) or ``header`` (variant only).
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def plan(batch_size: int = 10) -> dict:
    strata = json.loads((ROOT / "results/raw/strata.json").read_text())
    selected = {e["region_id"] for s in strata["reprise"]["strata"].values()
                for e in s["selection"]}
    todo = {"full": [], "header": []}
    for path in sorted((ROOT / "examples").glob("*/*/meta.json")):
        meta = json.loads(path.read_text())
        if meta["region_id"] not in selected \
                or meta.get("translation_status") != "final" \
                or (meta.get("validation") or {}).get("status") != "equivalent":
            continue
        rel = str(path.parent.relative_to(ROOT))
        opt = meta.get("optimization_status")
        if opt == "draft" and meta.get("optimization_notes"):
            continue
        if opt != "final":
            todo["full"].append(rel)
        elif meta.get("header_optimization_status") not in ("final", "draft"):
            todo["header"].append(rel)
    batches = []
    for kind in ("full", "header"):
        size = batch_size if kind == "full" else batch_size * 2
        regions = todo[kind]
        for i in range(0, len(regions), size):
            batches.append({"kind": kind, "regions": regions[i:i + size]})
    out = {"full": len(todo["full"]), "header": len(todo["header"]),
           "batches": batches}
    (ROOT / "results/summary/optimize_plan.json").write_text(
        json.dumps(out, indent=1) + "\n")
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch-size", type=int, default=10)
    r = plan(ap.parse_args().batch_size)
    print(f"to optimize: {r['full']} regions (both), {r['header']} "
          f"(header variant only); {len(r['batches'])} batches")
