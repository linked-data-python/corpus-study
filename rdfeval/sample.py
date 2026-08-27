"""Stratified, seeded sampling of RDF-relevant files.

Bands are defined over ``rdf_node_density`` in [sampling] of the config.
The sample is fully deterministic: candidates are sorted by a stable key
(repository, path) before ``random.Random(seed)`` draws, so re-running with
the same corpus and configuration yields the same sample.

Outputs:
    results/raw/sample.json    the sampled files per band + control group
"""

from __future__ import annotations

import json
import random
from collections import defaultdict

from .config import RESULTS_RAW, provenance
from .corpus import load_files_index

SAMPLE_PATH = RESULTS_RAW / "sample.json"


def band_of(density: float, cfg: dict) -> str | None:
    for band in ("low", "medium", "high"):
        lo, hi = cfg[f"band_{band}"]
        if lo <= density < hi or (band == "high" and density == hi):
            return band
    return None


def run(config: dict) -> None:
    cfg = config["sampling"]
    rng = random.Random(cfg["seed"])
    rows = [r for r in load_files_index()
            if r["rdf_ops"] > 0 and not r["error"]]
    # Only files whose repository allows snippet extraction can be translated;
    # others still count in corpus statistics but cannot enter the sample.
    from .select import load_manifest
    snippet_ok = {m["full_name"] for m in load_manifest() if m.get("snippet_ok")}
    eligible = [r for r in rows if r["repository"] in snippet_ok]

    by_band: dict[str, list[dict]] = defaultdict(list)
    for r in eligible:
        b = band_of(r["rdf_node_density"], cfg)
        if b:
            by_band[b].append(r)

    sample: dict[str, list[dict]] = {}
    for band in ("low", "medium", "high"):
        pool = sorted(by_band[band], key=lambda r: (r["repository"], r["path"]))
        want = cfg[f"sample_{band}"]
        cap = cfg["max_per_repo_per_band"]
        chosen: list[dict] = []
        per_repo: dict[str, int] = defaultdict(int)
        # rejection sampling under the per-repository cap
        indices = list(range(len(pool)))
        rng.shuffle(indices)
        for i in indices:
            r = pool[i]
            if per_repo[r["repository"]] >= cap:
                continue
            chosen.append(r)
            per_repo[r["repository"]] += 1
            if len(chosen) >= want:
                break
        sample[band] = sorted(chosen, key=lambda r: (r["repository"], r["path"]))
        if len(chosen) < want:
            print(f"  ! band {band}: only {len(chosen)}/{want} files available")

    # Control group: random low-density files NOT in the main sample.
    taken = {(r["repository"], r["path"]) for band in sample.values() for r in band}
    control_pool = sorted(
        (r for r in by_band["low"] if (r["repository"], r["path"]) not in taken),
        key=lambda r: (r["repository"], r["path"]))
    control = rng.sample(control_pool, min(cfg["control_sample"], len(control_pool)))

    out = {
        "provenance": provenance(config),
        "seed": cfg["seed"],
        "bands": {b: cfg[f"band_{b}"] for b in ("low", "medium", "high")},
        "population": {b: len(by_band[b]) for b in ("low", "medium", "high")},
        "eligible_files": len(eligible),
        "rdf_files_total": len(rows),
        "sample": {b: [{"repository": r["repository"], "path": r["path"],
                        "commit": r["commit"],
                        "rdf_node_density": r["rdf_node_density"],
                        "rdf_ops": r["rdf_ops"]} for r in sample[b]]
                   for b in sample},
        "control": [{"repository": r["repository"], "path": r["path"],
                     "commit": r["commit"],
                     "rdf_node_density": r["rdf_node_density"]}
                    for r in sorted(control, key=lambda r: (r["repository"], r["path"]))],
    }
    with open(SAMPLE_PATH, "w") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    print("sample:", {b: len(v) for b, v in sample.items()},
          f"+ {len(control)} control files (seed {cfg['seed']})")


def load_sample() -> dict:
    if not SAMPLE_PATH.exists():
        raise SystemExit("no sample; run `rdfeval sample` first")
    return json.loads(SAMPLE_PATH.read_text())
