"""Plan the translation batches of a campaign, reproducibly.

    python scripts/make_batches.py --per-stratum 6 --batch-size 3

Writes ``results/summary/batch_plan.json``: for each stratum, a seeded draw
of regions cut into batches of ``batch_size``.  Seeded and stable, so a wave
interrupted by a quota reset resumes exactly where it stopped, and a later
wave never re-assigns a region already done.

Regions already marked ``final`` are skipped: the plan is what is LEFT.
"""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLAN = ROOT / "results" / "summary" / "batch_plan.json"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-stratum", type=int, default=6,
                    help="regions to plan per stratum in this pass")
    ap.add_argument("--batch-size", type=int, default=3)
    ap.add_argument("--seed", type=int, default=20260828)
    args = ap.parse_args()

    examples = ROOT / "examples403"
    rng = random.Random(args.seed)
    plan: dict[str, list[list[str]]] = {}
    done_total = todo_total = 0
    for stratum_dir in sorted(examples.iterdir()):
        if not stratum_dir.is_dir():
            continue
        todo, done = [], 0
        for ex in sorted(stratum_dir.iterdir()):
            meta = ex / "meta.json"
            if not meta.exists():
                continue
            if json.loads(meta.read_text()).get("translation_status") == "final":
                done += 1
                continue
            todo.append(ex.name)
        done_total += done
        rng.shuffle(todo)
        picked = sorted(todo[:args.per_stratum])
        todo_total += len(picked)
        plan[stratum_dir.name] = [
            picked[i:i + args.batch_size]
            for i in range(0, len(picked), args.batch_size)]

    PLAN.parent.mkdir(parents=True, exist_ok=True)
    PLAN.write_text(json.dumps(
        {"seed": args.seed, "per_stratum": args.per_stratum,
         "batch_size": args.batch_size, "already_final": done_total,
         "planned": todo_total, "batches": plan}, indent=2), encoding="utf-8")
    print(f"plan: {todo_total} regions in "
          f"{sum(len(b) for b in plan.values())} batches "
          f"over {len(plan)} strata ({done_total} already final)")
    for stratum, batches in plan.items():
        print(f"  {stratum:24s} {sum(len(b) for b in batches):3d} regions "
              f"in {len(batches)} batches")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
