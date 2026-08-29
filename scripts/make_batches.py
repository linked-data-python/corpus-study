"""Plan the translation batches of a campaign, reproducibly.

    python scripts/make_batches.py --per-stratum 6 --batch-size 3
    python scripts/make_batches.py --target 6 --batch-size 3

Writes ``results/summary/batch_plan.json``: for each stratum, a seeded draw
of regions cut into batches of ``batch_size``.  Seeded and stable, so a wave
interrupted by a quota reset resumes exactly where it stopped, and a later
wave never re-assigns a region already done.

Regions already marked ``final`` are skipped: the plan is what is LEFT.

Two ways to size a wave, and they are not the same:

``--per-stratum N``
    N NEW regions for every stratum.  Uniform effort, and it **preserves**
    whatever imbalance the previous waves left: a stratum already at 21
    finals goes to 21 + N while one at 1 goes to 1 + N.

``--target N``
    Enough new regions to bring every stratum UP TO N finals in total —
    ``max(0, N - already_final)``.  Uniform result: a stratum already at or
    above N gets nothing.  This is what a balanced draw means, and what the
    per-stratum reading of the study needs, since a stratum that dominates
    the sample dominates the conclusions drawn from it.
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
    ap.add_argument("--per-stratum", type=int, default=None,
                    help="NEW regions to plan for every stratum in this pass")
    ap.add_argument("--target", type=int, default=None,
                    help="plan up to this TOTAL of final regions per stratum "
                         "(balances: a stratum already there gets nothing)")
    ap.add_argument("--batch-size", type=int, default=3)
    ap.add_argument("--seed", type=int, default=20260828)
    args = ap.parse_args()
    if (args.per_stratum is None) == (args.target is None):
        ap.error("give exactly one of --per-stratum or --target")

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
        want = (args.per_stratum if args.target is None
                else max(0, args.target - done))
        picked = sorted(todo[:want])
        todo_total += len(picked)
        plan[stratum_dir.name] = [
            picked[i:i + args.batch_size]
            for i in range(0, len(picked), args.batch_size)]

    PLAN.parent.mkdir(parents=True, exist_ok=True)
    PLAN.write_text(json.dumps(
        {"seed": args.seed, "per_stratum": args.per_stratum,
         "target": args.target,
         "batch_size": args.batch_size, "already_final": done_total,
         "planned": todo_total, "batches": plan}, indent=2), encoding="utf-8")
    print(f"plan: {todo_total} regions in "
          f"{sum(len(b) for b in plan.values())} batches "
          f"over {len(plan)} strata ({done_total} already final)")
    for stratum, batches in plan.items():
        n = sum(len(b) for b in batches)
        print(f"  {stratum:24s} {n:3d} regions "
              f"in {len(batches)} batches" + ("" if n else "   (already there)"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
