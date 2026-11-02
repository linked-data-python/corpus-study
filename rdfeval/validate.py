"""Run every example's validation driver and record the verdicts.

Only examples whose ``meta.json`` has ``translation_status: "final"`` are
validated.  Each driver runs in a subprocess (own interpreter, timeout from
config) and prints a ``RDFEVAL-VERDICT`` line that this stage collects into

    results/raw/validation.jsonl

and mirrors into each example's ``meta.json`` (``validation`` key).  An
example with no runnable driver (or a failing one) is *not* dropped: it is
recorded with ``status: "unresolved"`` and the reason.

A region whose ``optimization_status`` is ``"final"`` also has its two
optimized artefacts validated, each against ``original.py`` with the same
driver (``RDFEVAL_SIDES``), under ``validation_optimized`` in ``meta.json``
and as extra rows (``artefact`` column) in the same file.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys

from .config import EXAMPLES_DIR, RESULTS_RAW, provenance
from .harness import DEFAULT_SIDES, SIDES_ENV
from .study import Study, STUDY

VALIDATION_PATH = RESULTS_RAW / "validation.jsonl"


def iter_examples(study: Study = STUDY):
    root = study.examples_dir
    if not root.exists():
        return
    for band_dir in sorted(root.iterdir()):
        if not band_dir.is_dir():
            continue
        for ex_dir in sorted(band_dir.iterdir()):
            meta_path = ex_dir / "meta.json"
            if meta_path.exists():
                yield ex_dir, json.loads(meta_path.read_text())


OPTIMIZED = ("optimized.py", "optimized.ldpy")
HEADER = ("optimized_header.py", "optimized_header.ldpy")


def _run_driver(ex_dir, timeout: int,
                sides: tuple[str, str] = DEFAULT_SIDES) -> dict:
    proc = subprocess.run(
        [sys.executable, str(ex_dir / "driver.py")],
        capture_output=True, text=True, timeout=timeout,
        cwd=ex_dir, env={**os.environ, SIDES_ENV: ",".join(sides)},
    )
    for line in proc.stderr.splitlines():
        if line.startswith("RDFEVAL-VERDICT "):
            return json.loads(line[len("RDFEVAL-VERDICT "):])
    return {"equivalent": False, "error":
            f"driver produced no verdict (rc={proc.returncode}): "
            + (proc.stderr.strip()[-500:] or proc.stdout.strip()[-500:])}


def _status(verdict: dict) -> str:
    if verdict.get("error"):
        return "unresolved"
    return "equivalent" if verdict["equivalent"] else "not-equivalent"


def _validate_optimized(ex_dir, timeout: int) -> dict:
    """Each optimized artefact against the original, with the same driver."""
    out = {}
    for name in OPTIMIZED + HEADER:
        if not (ex_dir / name).exists():
            if name not in HEADER:          # the header variant is optional
                out[name] = {"status": "unresolved", "error": f"no {name}"}
            continue
        try:
            verdict = _run_driver(ex_dir, timeout, ("original.py", name))
        except subprocess.TimeoutExpired:
            verdict = {"equivalent": False, "error": f"timeout ({timeout}s)"}
        out[name] = {"status": _status(verdict),
                     "method": verdict.get("method"),
                     "diffs": verdict.get("diffs", []),
                     "error": verdict.get("error")}
    return out


def run(config: dict, study: Study = STUDY) -> None:
    timeout = config["validation"]["timeout_seconds"]
    rows = []
    regressions: list[tuple[str, str]] = []
    counts = {"equivalent": 0, "not-equivalent": 0, "unresolved": 0, "skipped": 0}
    counts_opt = {"equivalent": 0, "not-equivalent": 0, "unresolved": 0}
    for ex_dir, meta in iter_examples(study):
        rid = meta["region_id"]
        if meta.get("translation_status") != "final":
            counts["skipped"] += 1
            continue
        if meta.get("classification") in ("not-expressible", "excluded"):
            counts["skipped"] += 1
            continue
        try:
            verdict = _run_driver(ex_dir, timeout)
        except subprocess.TimeoutExpired:
            verdict = {"equivalent": False, "error": f"timeout ({timeout}s)"}
        status = _status(verdict)
        counts[status] += 1
        row = {"region_id": rid, study.group: meta[study.group],
               "status": status, **verdict}
        rows.append(row)
        meta["validation"] = {"status": status,
                              "method": verdict.get("method"),
                              "diffs": verdict.get("diffs", []),
                              "error": verdict.get("error")}
        if verdict.get("names_only_original"):
            meta["validation"]["names_only_original"] = \
                verdict["names_only_original"]
        if meta.get("optimization_status") == "final":
            meta["validation_optimized"] = _validate_optimized(
                ex_dir, timeout)
            for name, v in meta["validation_optimized"].items():
                counts_opt[v["status"]] += 1
                rows.append({"region_id": rid, study.group: meta[study.group],
                             "artefact": name, **v})
                if v["status"] != "equivalent":
                    print(f"  ✗ {rid} [{name}] — "
                          f"{v.get('diffs') or v.get('error', '')}")
        (ex_dir / "meta.json").write_text(
            json.dumps(meta, indent=2, ensure_ascii=False))
        mark = {"equivalent": "✓", "not-equivalent": "✗", "unresolved": "?"}[status]
        print(f"  {mark} {rid}"
              + (f" — {verdict.get('diffs') or verdict.get('error', '')}"
                 if status != "equivalent" else ""))
    out_path = study.path(VALIDATION_PATH)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        f.write(json.dumps({"provenance": provenance(config)}) + "\n")
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(f"validate: {counts}")
    if any(counts_opt.values()):
        print(f"validate (optimized artefacts): {counts_opt}")
    if regressions:
        print(f"  !! {len(regressions)} pair(s) that were EQUIVALENT no longer "
              f"are. Check the environment before trusting this run — a "
              f"missing dependency looks exactly like this:")
        for rid, err in regressions[:5]:
            print(f"     {rid}: {err}")
