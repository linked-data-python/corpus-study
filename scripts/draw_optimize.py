"""Draw the regions whose optimized artefacts are written (record corpus/403).

    python scripts/draw_optimize.py

Five regions per stratum, among the pairs of the resumed selection (record
corpus/404) proved equivalent. A region that already carries optimized
artefacts and still belongs to the stratum's selection is kept, and
rewritten by the same model as the others; the rest is a seeded draw. One
region per stratum — the kept one, else the first drawn — is the model
check: a second model writes its artefacts too, to see whether the share
between rereading and notation depends on the model.

Writes ``results/raw/optimize_sample.json``.
"""

from __future__ import annotations

import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SEED = 20261103
PER_STRATUM = 5


def main() -> dict:
    strata = json.loads((ROOT / "results/raw/strata.json").read_text())
    selection = {k: {e["region_id"] for e in s["selection"]}
                 for k, s in strata["reprise"]["strata"].items()}
    metas = {}
    for path in sorted((ROOT / "examples").glob("*/*/meta.json")):
        meta = json.loads(path.read_text())
        metas[meta["region_id"]] = (path.parent, meta)
    proved = {rid for rid, (_, m) in metas.items()
              if m.get("translation_status") == "final"
              and (m.get("validation") or {}).get("status") == "equivalent"}
    rng = random.Random(SEED)
    taken: set[str] = set()
    out: dict[str, list] = {}
    for kind in sorted(selection):
        pool = sorted(selection[kind] & proved)
        kept = [r for r in pool if metas[r][1].get("optimization_status")
                and metas[r][0].parent.name == kind and r not in taken]
        rng.shuffle(pool)
        chosen = kept[:PER_STRATUM]
        for rid in pool:
            if len(chosen) >= PER_STRATUM:
                break
            if rid not in taken and rid not in chosen:
                chosen.append(rid)
        taken.update(chosen)
        out[kind] = [{"region_id": rid,
                      "dir": str(metas[rid][0].relative_to(ROOT)),
                      "kept": rid in kept,
                      "model_check": i == 0}
                     for i, rid in enumerate(chosen)]
    result = {"seed": SEED, "per_stratum": PER_STRATUM, "strata": out}
    (ROOT / "results/raw/optimize_sample.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    return result


if __name__ == "__main__":
    r = main()
    n = sum(len(v) for v in r["strata"].values())
    print(f"optimize sample: {n} regions, "
          f"{sum(e['kept'] for v in r['strata'].values() for e in v)} kept, "
          f"{sum(e['model_check'] for v in r['strata'].values() for e in v)}"
          " for the model check")
