"""Validity audit of the RDF-usage analyser.

The detector's precision underpins every downstream number, so it is
itself measured rather than assumed.  This stage draws a seeded random
sample of detected operations across the whole corpus, writes each with its
source line and enough context to be judged by a human, and re-checks the
control files of the sampling stage.

    results/raw/audit_sample.jsonl   operations to inspect (+ verdict slot)
    results/summary/audit.json       counts once verdicts are filled in

Filling ``verdict`` with "true-positive" / "false-positive" in the JSONL
and re-running the stage computes precision.  Nothing is inferred
automatically: an unjudged sample yields "precision: null", never a guess.

The complementary direction (recall) is approximated by ``negative_probe``:
files that import rdflib but where the analyser found *no* operation are
listed, since those are exactly where a missed pattern would hide.
"""

from __future__ import annotations

import json
import random

from .acquire import repo_dir
from .config import RESULTS_RAW, RESULTS_SUMMARY, provenance
from .corpus import ANALYSIS_DIR, load_files_index

AUDIT_SAMPLE = RESULTS_RAW / "audit_sample.jsonl"
AUDIT_NEGATIVES = RESULTS_RAW / "audit_negatives.jsonl"
AUDIT_SUMMARY = RESULTS_SUMMARY / "audit.json"

NEGATIVE_SAMPLE_SIZE = 25


def _load_negative_verdicts() -> dict[str, str]:
    """Verdicts on the negative sample ("miss" / "correct-negative")."""
    if not AUDIT_NEGATIVES.exists():
        return {}
    out = {}
    for line in AUDIT_NEGATIVES.read_text().splitlines():
        if not line.strip():
            continue
        rec = json.loads(line)
        if rec.get("neg_id") and rec.get("verdict"):
            out[rec["neg_id"]] = rec["verdict"]
    return out


def _load_ops(config: dict, row: dict) -> list[dict]:
    """Re-analyse one file to recover its individual operations."""
    from .analyze import analyze_file
    path = repo_dir(config, row["repository"]) / row["path"]
    fa = analyze_file(path)
    return [op.to_dict() for op in fa.ops]


def _source_line(config: dict, row: dict, lineno: int) -> str:
    path = repo_dir(config, row["repository"]) / row["path"]
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return ""
    return lines[lineno - 1].strip() if 0 < lineno <= len(lines) else ""


def load_existing_verdicts() -> dict[str, str]:
    """Verdicts already recorded, keyed by operation id (survives re-runs)."""
    if not AUDIT_SAMPLE.exists():
        return {}
    out = {}
    for line in AUDIT_SAMPLE.read_text().splitlines():
        if not line.strip():
            continue
        rec = json.loads(line)
        if rec.get("op_id") and rec.get("verdict"):
            out[rec["op_id"]] = rec["verdict"]
    return out


def _stable_key(identifier: str, seed: int) -> int:
    """Deterministic hash of an identifier (stable across runs and machines).

    Selection by hash rather than by draw order keeps the audit sample —
    and therefore the manual verdicts already recorded against it — stable
    when the corpus index changes.
    """
    import hashlib
    h = hashlib.sha256(f"{seed}:{identifier}".encode()).hexdigest()
    return int(h[:12], 16)


def run(config: dict, sample_size: int = 120) -> None:
    rows = sorted((r for r in load_files_index()
                   if r["rdf_ops"] > 0 and not r["error"]),
                  key=lambda r: (r["repository"], r["path"]))
    seed = config["sampling"]["seed"]
    rng = random.Random(seed)
    verdicts = load_existing_verdicts()

    # Stable sample: rank files by hash, walk them in that order, and take
    # the hash-lowest operation of each until the sample is full.  Files and
    # operations already judged keep their verdicts.
    ranked_files = sorted(rows, key=lambda r: _stable_key(
        f"{r['repository']}:{r['path']}", seed))
    records = []
    for row in ranked_files:
        ops = _load_ops(config, row)
        if not ops:
            continue
        op = min(ops, key=lambda o: _stable_key(
            f"{row['repository']}:{row['path']}:{o['lineno']}:{o['category']}",
            seed))
        op_id = f"{row['repository']}:{row['path']}:{op['lineno']}:{op['category']}"
        records.append({
            "op_id": op_id,
            "repository": row["repository"], "commit": row["commit"],
            "path": row["path"], "lineno": op["lineno"],
            "category": op["category"], "detail": op["detail"],
            "certain": op["certain"],
            "source_line": _source_line(config, row, op["lineno"]),
            "verdict": verdicts.get(op_id),   # "true-positive"/"false-positive"
        })
        if len(records) >= sample_size:
            break

    # negative probe: files importing rdflib with zero detected operations.
    # A seeded sample of these is judged by hand (does the file really
    # contain RDF operations?) to bound the analyser's recall.
    negatives = sorted(
        ({"repository": r["repository"], "path": r["path"]}
         for r in load_files_index()
         if r["imports_rdflib"] and r["rdf_ops"] == 0 and not r["error"]),
        key=lambda n: _stable_key(f"{n['repository']}:{n['path']}", seed))
    neg_verdicts = _load_negative_verdicts()
    negative_sample = [
        {**n, "neg_id": f"{n['repository']}:{n['path']}",
         "verdict": neg_verdicts.get(f"{n['repository']}:{n['path']}")}
        for n in negatives[:NEGATIVE_SAMPLE_SIZE]]

    AUDIT_SAMPLE.parent.mkdir(parents=True, exist_ok=True)
    with open(AUDIT_SAMPLE, "w") as f:
        f.write(json.dumps({"provenance": provenance(config),
                            "instructions":
                            "set \"verdict\" to true-positive or "
                            "false-positive for each record, then re-run "
                            "`rdfeval audit` to compute precision"}) + "\n")
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    judged = [r for r in records if r["verdict"]]
    tp = sum(1 for r in judged if r["verdict"] == "true-positive")
    summary = {
        "provenance": provenance(config),
        "sampled_operations": len(records),
        "judged_operations": len(judged),
        "precision": round(tp / len(judged), 4) if judged else None,
        "by_category": _by_category(records),
        "uncertain_share": round(
            sum(1 for r in records if not r["certain"]) / len(records), 4)
        if records else None,
        "negative_probe": {
            "files_importing_rdflib_without_operations": len(negatives),
            "sampled": len(negative_sample),
            "judged": sum(1 for n in negative_sample if n["verdict"]),
            "misses": sum(1 for n in negative_sample
                          if n["verdict"] == "miss"),
            "file_level_miss_rate": (
                round(sum(1 for n in negative_sample if n["verdict"] == "miss")
                      / sum(1 for n in negative_sample if n["verdict"]), 4)
                if any(n["verdict"] for n in negative_sample) else None),
        },
    }
    with open(AUDIT_NEGATIVES, "w") as f:
        f.write(json.dumps({"provenance": provenance(config),
                            "instructions":
                            "set \"verdict\" to miss (the file does contain "
                            "RDF operations the analyser did not detect) or "
                            "correct-negative (no RDF operation: unused "
                            "import, non-RDF .add, etc.)"}) + "\n")
        for rec in negative_sample:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    AUDIT_SUMMARY.parent.mkdir(parents=True, exist_ok=True)
    with open(AUDIT_SUMMARY, "w") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(f"audit: {len(records)} operations sampled "
          f"({len(judged)} judged, precision "
          f"{summary['precision'] if summary['precision'] is not None else 'n/a'}), "
          f"{len(negatives)} rdflib-importing files with no operation")


def _by_category(records: list[dict]) -> dict:
    out: dict[str, dict] = {}
    for r in records:
        d = out.setdefault(r["category"], {"sampled": 0, "judged": 0, "tp": 0})
        d["sampled"] += 1
        if r["verdict"]:
            d["judged"] += 1
            d["tp"] += int(r["verdict"] == "true-positive")
    for d in out.values():
        d["precision"] = round(d["tp"] / d["judged"], 4) if d["judged"] else None
    return dict(sorted(out.items()))
