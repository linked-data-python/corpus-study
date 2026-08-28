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


def draw_wave(pool: list[dict], already: set[tuple[str, str]], want: int,
              cap: int, rng: random.Random) -> list[dict]:
    """Draw up to ``want`` files from ``pool``, keeping those already drawn.

    The sample grows in *waves*: enlarging a quota never re-draws, it tops
    up.  Files of ``already`` are retained and count towards both ``want``
    and the per-repository cap, so a wave-2 sample is a superset of wave 1
    and the translations reviewed under wave 1 stay valid.
    """
    key = lambda r: (r["repository"], r["path"])          # noqa: E731
    pool = sorted(pool, key=key)
    kept = [r for r in pool if key(r) in already]
    per_repo: dict[str, int] = defaultdict(int)
    for r in kept:
        per_repo[r["repository"]] += 1
    chosen = list(kept)
    indices = list(range(len(pool)))
    rng.shuffle(indices)
    for i in indices:
        if len(chosen) >= want:
            break
        r = pool[i]
        if key(r) in already or per_repo[r["repository"]] >= cap:
            continue
        chosen.append(r)
        per_repo[r["repository"]] += 1
    return sorted(chosen, key=key)


def _previous_selection() -> dict[str, set[tuple[str, str]]]:
    """Files drawn by earlier waves, per band (empty on a first run)."""
    if not SAMPLE_PATH.exists():
        return {}
    prev = json.loads(SAMPLE_PATH.read_text())
    return {band: {(f["repository"], f["path"]) for f in files}
            for band, files in prev.get("sample", {}).items()}


def run(config: dict) -> None:
    cfg = config["sampling"]
    rng = random.Random(cfg["seed"])
    previous = _previous_selection()
    rows = [r for r in load_files_index()
            if r["rdf_ops"] > 0 and not r["error"]]
    # Only files whose repository allows snippet extraction can be translated;
    # others still count in corpus statistics but cannot enter the sample.
    # Repositories pruned after analysis (no analysable RDF Python) are out too.
    from .select import load_manifest
    snippet_ok = {m["full_name"] for m in load_manifest()
                  if m.get("snippet_ok") and not m.get("pruned")}
    eligible = [r for r in rows if r["repository"] in snippet_ok]

    by_band: dict[str, list[dict]] = defaultdict(list)
    for r in eligible:
        b = band_of(r["rdf_node_density"], cfg)
        if b:
            by_band[b].append(r)

    sample: dict[str, list[dict]] = {}
    added: dict[str, int] = {}
    for band in ("low", "medium", "high"):
        want = cfg[f"sample_{band}"]
        already = previous.get(band, set())
        chosen = draw_wave(by_band[band], already, want,
                           cfg["max_per_repo_per_band"], rng)
        sample[band] = chosen
        added[band] = len(chosen) - len(already)
        if len(chosen) < want:
            print(f"  ! band {band}: only {len(chosen)}/{want} files available")
        missing = already - {(r["repository"], r["path"]) for r in chosen}
        if missing:
            # a previously sampled file left the pool (corpus re-analysed):
            # never silently drop it — the reader must know
            print(f"  ! band {band}: {len(missing)} previously sampled file(s) "
                  f"are no longer in the pool: {sorted(missing)[:3]}")

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
    out["wave_added"] = added
    with open(SAMPLE_PATH, "w") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    print("sample:", {b: len(v) for b, v in sample.items()},
          f"(+{sum(added.values())} this wave)",
          f"+ {len(control)} control files (seed {cfg['seed']})")


def load_sample() -> dict:
    if not SAMPLE_PATH.exists():
        raise SystemExit("no sample; run `rdfeval sample` first")
    return json.loads(SAMPLE_PATH.read_text())
