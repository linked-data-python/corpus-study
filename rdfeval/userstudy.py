"""Export validated pairs as user-study task material.

Selects semantically-validated examples, balanced across the study's own
grouping — **strata of use** —
and produces ``../user_study/config/tasks.generated.json``: for each example,
both representations plus automatically derived comprehension facts.
Question texts are generated as *drafts* for the researchers to review — the
study never runs on unreviewed material.

Two kinds of region need two kinds of observable, and the split is the one
the validation oracle already makes (record corpus/405).  A region that
**writes** RDF is asked about the triples it produces; a region that
**reads** one is asked about the value it returns from a fixture graph, since
it may add no triple at all.  Asking a reading region how many triples it
adds would be a question with no answer.

Traceability: every task keeps region_id → repository/commit/path, its
stratum or band, and the constructions the translation declares.
"""

from __future__ import annotations

import contextlib
import io
import json
import os
import random
import sys
from pathlib import Path

from .config import ROOT, provenance
from .study import STUDY, Study
from .validate import iter_examples

OUT_PATH = ROOT.parent / "user_study" / "config" / "tasks.generated.json"


def _n3(term, nm=None):
    try:
        return term.n3(nm) if nm is not None else term.n3()
    except Exception:
        return str(term)


@contextlib.contextmanager
def _in_example(ex_dir):
    """Run inside an example directory, as its validation subprocess does.

    The pairs import sibling modules of their own directory (`brick_context`,
    `orm_context`): the real validation runs a subprocess with `cwd=ex_dir`,
    which puts that directory on the import path. Here we are in-process, so
    both have to be arranged and undone.
    """
    cwd = os.getcwd()
    os.chdir(ex_dir)
    sys.path.insert(0, str(ex_dir))
    try:
        yield
    finally:
        with contextlib.suppress(ValueError):
            sys.path.remove(str(ex_dir))
        os.chdir(cwd)


def _driver_spec(ex_dir) -> dict | None:
    """How this pair is exercised, taken from its validation driver.

    The driver already states the entry point, the fixture and the call
    cases; reading them back by parsing its text would be a second source of
    truth that drifts. Instead the driver is executed with ``run_pair``
    replaced by a recorder — the same file, its own words.
    """
    ex_dir = Path(ex_dir).resolve()      # chdir below: relative paths break
    driver = ex_dir / "driver.py"
    if not driver.exists():
        return None
    from . import harness
    captured: dict = {}

    def _record(driver_file, **kw):
        captured.update(kw)
        return {"equivalent": True}

    real, harness.run_pair = harness.run_pair, _record
    try:
        with _in_example(ex_dir), contextlib.redirect_stdout(io.StringIO()):
            exec(compile(driver.read_text(), str(driver), "exec"),
                 {"__name__": "__driver__", "__file__": str(driver)})
    except Exception:
        return None
    finally:
        harness.run_pair = real
    return captured


def _call_cases(ex_dir, spec):
    """The argument cases the driver defines, as the harness builds them."""
    from .harness import fixture_graph
    calls = spec.get("calls")
    if calls:
        return calls
    fixture = spec.get("fixture")
    if fixture:
        path = Path(ex_dir).resolve() / fixture
        return [lambda: ((fixture_graph(path),), {})]
    return None


def _observables(ex_dir, meta):
    """What the region SHOWS, exercised exactly as the validation exercises it.

    Returns ``(triples, value)``. Which of the two a region offers is decided
    by what it actually produces, not by its oracle: a region filed under a
    reading stratum may still *return a graph*, and the graph's triples are
    then the answerable fact. A region file defines a function — importing it
    builds nothing — so the entry point is called with the driver's own
    fixture.
    """
    from .harness import materialise, normalise
    ex_dir = Path(ex_dir).resolve()      # chdir below: relative paths break
    py_path = ex_dir / "original.py"
    spec = _driver_spec(ex_dir) or {}
    entry = spec.get("entry")

    ns: dict = {"__name__": "__task__", "__file__": str(py_path)}
    with _in_example(ex_dir):
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                exec(compile(py_path.read_text(), str(py_path), "exec"), ns)
            graphs: list = []
            returned = None
            if entry and callable(ns.get(entry)):
                cases = _call_cases(ex_dir, spec) or [((), {})]
                case = cases[0]
                args, kw = case() if callable(case) else case
                # a region commonly mutates a graph it receives — as a
                # positional argument or, just as often, as `graph=`
                given = [v for v in list(args) + list(kw.values())
                         if _is_graph(v)]
                before = {id(g): len(g) for g in given}
                with contextlib.redirect_stdout(io.StringIO()):
                    returned = materialise(ns[entry](*args, **kw))
                if _is_graph(returned):
                    graphs.append(returned)
                # a given graph counts only if the region WROTE to it: the
                # fixture it merely read is the question's input, not its
                # answer
                graphs += [g for g in given if len(g) != before[id(g)]]
            graphs += [v for v in ns.values() if _is_graph(v)]
        except Exception:
            return None, None

    triples = _triples_of(graphs)
    if triples:
        return triples, None
    if returned is None or _is_graph(returned):
        return None, None
    try:
        return None, json.loads(json.dumps(normalise(returned), default=str))
    except Exception:
        return None, None


def _is_graph(v) -> bool:
    from rdflib import Graph
    return isinstance(v, Graph)


def _triples_of(graphs) -> list[tuple[str, str, str]] | None:
    out = []
    for g in graphs:
        for s, p, o in g:
            out.append((_n3(s, g.namespace_manager),
                        _n3(p, g.namespace_manager),
                        _n3(o, g.namespace_manager)))
    return sorted(set(out)) or None


def _draft_questions(triples, value, rng: random.Random) -> list[dict]:
    """Draft prompts, chosen by what the region actually shows."""
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
    elif value is not None:
        # how many the region finds is gradable and readable whatever the
        # shape of the result; quoting a large structure back at the
        # participant is neither
        if isinstance(value, (list, dict)):
            qs.append({
                "type": "count",
                "prompt_draft": ("How many entries does the result of this "
                                 "region have, on the input graph shown?"
                                 if isinstance(value, dict) else
                                 "How many results does this region find in "
                                 "the input graph?"),
                "answer": len(value),
            })
        if isinstance(value, (str, int, float, bool)) or (
                isinstance(value, list) and len(value) <= 4
                and all(isinstance(v, (str, int, float, bool)) for v in value)):
            qs.append({
                "type": "returned-value",
                "prompt_draft": "Given the input graph shown, what does this "
                                "region return?",
                "answer": value,
            })
    qs.append({
        "type": "modify",
        "prompt_draft": "Modify the program so that it additionally asserts "
                        "the RDF relationship specified by the experimenter.",
        "answer": None,
        "needs_review": True,
    })
    return qs


def run(config: dict, study: Study = STUDY) -> None:
    rng = random.Random(config["sampling"]["seed"])
    max_tasks = config["userstudy"]["max_tasks"]
    group_key = study.group
    candidates = []
    for ex_dir, meta in iter_examples(study):
        if (meta.get("validation") or {}).get("status") != "equivalent":
            continue
        candidates.append((ex_dir, meta))

    # balance across the study's own grouping, deterministic order then
    # seeded shuffle
    by_group: dict[str, list] = {}
    for ex_dir, meta in candidates:
        by_group.setdefault(meta[group_key], []).append((ex_dir, meta))
    groups = sorted(by_group)
    for group in groups:
        by_group[group].sort(key=lambda x: x[1]["region_id"])
        rng.shuffle(by_group[group])

    # a quota per group, then the remainder distributed over the groups that
    # still have material: a stratum with two validated regions must not cap
    # the whole export at two per stratum.
    per = max_tasks // len(groups) if groups else 0
    chosen: list = []
    for group in groups:
        chosen.extend((group, x) for x in by_group[group][:per])
    if len(chosen) < max_tasks:
        for group in groups:
            for x in by_group[group][per:]:
                if len(chosen) >= max_tasks:
                    break
                chosen.append((group, x))
            if len(chosen) >= max_tasks:
                break

    tasks = []
    for group, (ex_dir, meta) in chosen:
        reads = (meta.get("oracle") == "values")
        triples, value = _observables(ex_dir, meta)
        fixture = (_driver_spec(ex_dir) or {}).get("fixture")
        task = {
            "task_id": f"task-{meta['region_id']}",
            "region_id": meta["region_id"],
            "repository": meta["repository"],
            "commit": meta["commit"],
            "path": meta["path"],
            group_key: group,
            "study": study.name,
            "oracle": meta.get("oracle", "isomorphism"),
            "constructions": meta.get("constructions", []),
            "representations": {
                "rdflib": (ex_dir / "original.py").read_text(),
                "ldpy": (ex_dir / "translated.ldpy").read_text(),
            },
            "derived_triples": triples,
            "derived_value": value,
            # what could be derived automatically. "none" means the region
            # could not be exercised in-process — it needs context the
            # example directory does not carry (a network service, a
            # database, a package of its own repository). Its comprehension
            # questions have to be written by hand before the task is
            # usable; the review step is where that happens.
            "derivation": ("triples" if triples
                           else "value" if value is not None else "none"),
            "questions_draft": _draft_questions(triples, value, rng),
            "review_status": "draft",
        }
        if reads and fixture and (ex_dir / fixture).exists():
            # a reading task is unanswerable without the graph it reads
            task["input_graph"] = (ex_dir / fixture).read_text()
        tasks.append(task)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_PATH, "w") as f:
        json.dump({"provenance": provenance(config),
                   "study": study.name,
                   "note": "DRAFT task material — review before any study run",
                   "tasks": tasks}, f, indent=2, ensure_ascii=False)
    reading = sum(1 for t in tasks if t["oracle"] == "values")
    derived = sum(1 for t in tasks if t["derivation"] != "none")
    plural = {"band": "bands", "stratum": "strata"}.get(group_key,
                                                        group_key + "s")
    print("userstudy: %d draft tasks (%d reading, %d construction) "
          "over %d %s -> %s"
          % (len(tasks), reading, len(tasks) - reading,
             len({t[group_key] for t in tasks}), plural, OUT_PATH))
    print("userstudy: %d of %d carry automatically derived facts; the other "
          "%d need their questions written by hand at review"
          % (derived, len(tasks), len(tasks) - derived))
