"""Export validated pairs as user-study task material.

Selects semantically-validated examples (balanced across density bands),
and produces ``../user_study/config/tasks.generated.json``: for each
example, both representations plus automatically derived comprehension
facts (the triples the code actually builds, captured by executing the
validated original).  Question texts are generated as *drafts* for the
researchers to review — the study never runs on unreviewed material.

Traceability: every task keeps region_id → repository/commit/path.
"""

from __future__ import annotations

import contextlib
import io
import json
import random

from .config import ROOT, provenance
from .validate import iter_examples

OUT_PATH = ROOT.parent / "user_study" / "config" / "tasks.generated.json"


def _module_triples(py_path) -> list[tuple[str, str, str]] | None:
    """Execute the original module and return the union of its graphs' triples
    in N3 notation (None if nothing observable)."""
    from rdflib import Graph
    ns: dict = {"__name__": "__task__", "__file__": str(py_path)}
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            exec(compile(py_path.read_text(), str(py_path), "exec"), ns)
    except Exception:
        return None
    triples = []
    for v in ns.values():
        if isinstance(v, Graph):
            for s, p, o in v:
                triples.append((s.n3(v.namespace_manager),
                                p.n3(v.namespace_manager),
                                o.n3(v.namespace_manager)))
    return sorted(set(triples)) or None


def _draft_questions(triples: list[tuple[str, str, str]] | None,
                     rng: random.Random) -> list[dict]:
    qs: list[dict] = []
    if triples:
        qs.append({
            "type": "count",
            "prompt_draft": "How many RDF triples does this code add to the graph?",
            "answer": len(triples),
        })
        s, p, o = rng.choice(triples)
        qs.append({
            "type": "predicate-object",
            "prompt_draft": f"Which value does the property {p} of {s} take?",
            "answer": o,
            "distractor_pool": sorted({t[2] for t in triples if t[2] != o})[:3],
        })
        qs.append({
            "type": "triple-membership",
            "prompt_draft": "Does the code produce the triple "
                            f"{s} {p} {o} ?",
            "answer": True,
        })
    qs.append({
        "type": "modify",
        "prompt_draft": "Modify the program so that it additionally asserts "
                        "the RDF relationship specified by the experimenter.",
        "answer": None,
        "needs_review": True,
    })
    return qs


def run(config: dict) -> None:
    rng = random.Random(config["sampling"]["seed"])
    max_tasks = config["userstudy"]["max_tasks"]
    candidates = []
    for ex_dir, meta in iter_examples():
        if (meta.get("validation") or {}).get("status") != "equivalent":
            continue
        candidates.append((ex_dir, meta))
    # balance across bands, deterministic order then seeded shuffle
    by_band: dict[str, list] = {}
    for ex_dir, meta in candidates:
        by_band.setdefault(meta["band"], []).append((ex_dir, meta))
    tasks = []
    bands = sorted(by_band)
    for band in bands:
        by_band[band].sort(key=lambda x: x[1]["region_id"])
        rng.shuffle(by_band[band])
    quota = {b: max_tasks // len(bands) if bands else 0 for b in bands}
    for band in bands:
        for ex_dir, meta in by_band[band][:quota[band]]:
            triples = _module_triples(ex_dir / "original.py")
            tasks.append({
                "task_id": f"task-{meta['region_id']}",
                "region_id": meta["region_id"],
                "repository": meta["repository"],
                "commit": meta["commit"],
                "path": meta["path"],
                "band": band,
                "representations": {
                    "rdflib": (ex_dir / "original.py").read_text(),
                    "ldpy": (ex_dir / "translated.ldpy").read_text(),
                },
                "derived_triples": triples,
                "questions_draft": _draft_questions(triples, rng),
                "review_status": "draft",
            })
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_PATH, "w") as f:
        json.dump({"provenance": provenance(config),
                   "note": "DRAFT task material — review before any study run",
                   "tasks": tasks}, f, indent=2, ensure_ascii=False)
    print(f"userstudy: {len(tasks)} draft tasks -> {OUT_PATH}")
