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
import re
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

    Returns ``(triples, value, removed)``. Which a region offers is decided
    by what it actually produces, not by its oracle: a region filed under a
    reading stratum may still *return a graph*, and the graph's triples are
    then the answerable fact. A region file defines a function — importing it
    builds nothing — so the entry point is called with the driver's own
    fixture.

    A graph the region is GIVEN counts by what the region changed in it: the
    triples it added — those already there are the question's input, shown
    to the participant, not its answer — or, for a region that only deletes,
    the triples it removed.
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
            added: list = []
            removed: list = []
            if entry and callable(ns.get(entry)):
                cases = _call_cases(ex_dir, spec) or [((), {})]
                case = cases[0]
                args, kw = case() if callable(case) else case
                # a region commonly mutates a graph it receives — as a
                # positional argument or, just as often, as `graph=`
                given = [v for v in list(args) + list(kw.values())
                         if _is_graph(v)]
                before = {id(g): set(g) for g in given}
                with contextlib.redirect_stdout(io.StringIO()):
                    returned = materialise(ns[entry](*args, **kw))
                if _is_graph(returned) and id(returned) not in before:
                    graphs.append(returned)
                # a given graph counts only by what the region CHANGED in
                # it: the fixture it merely read is the question's input,
                # not its answer
                for g in given:
                    now = set(g)
                    added += [(g, t) for t in now - before[id(g)]]
                    removed += [(g, t) for t in before[id(g)] - now]
            graphs += [v for v in ns.values() if _is_graph(v)]
        except Exception:
            return None, None, None

    triples = _merge(_triples_of(graphs), _changed(added))
    if triples:
        return triples, None, None
    if removed:
        return None, None, _changed(removed)
    if returned is None or _is_graph(returned):
        return None, None, None
    try:
        return (None, json.loads(json.dumps(normalise(returned), default=str)),
                None)
    except Exception:
        return None, None, None


def _changed(pairs) -> list[tuple[str, str, str]] | None:
    out = {tuple(_n3(x, g.namespace_manager) for x in t) for g, t in pairs}
    return sorted(out) or None


def _merge(a, b):
    return sorted(set(a or ()) | set(b or ())) or None


class _Opaque(Exception):
    """An argument that cannot be written back as Python source."""


def _py(v, indent: int = 0, width: int = 72) -> str:
    """``v`` as Python source a participant can read, or :class:`_Opaque`."""
    from types import SimpleNamespace
    from rdflib import BNode, Literal, URIRef
    if v is None or isinstance(v, (bool, int, float)):
        return repr(v)
    if isinstance(v, URIRef):
        return f"URIRef({str(v)!r})"
    if isinstance(v, BNode):
        return f"BNode({str(v)!r})"
    if isinstance(v, Literal):
        parts = [repr(str(v))]
        if v.language:
            parts.append(f"lang={v.language!r}")
        elif v.datatype:
            parts.append(f"datatype=URIRef({str(v.datatype)!r})")
        return f"Literal({', '.join(parts)})"
    if isinstance(v, str):
        return repr(v)
    if isinstance(v, SimpleNamespace):
        items = [f"{k}={_py(x, indent + 4, width)}" for k, x in vars(v).items()]
        return _wrap("SimpleNamespace(", items, ")", indent, width)
    if isinstance(v, dict):
        items = [f"{_py(k)}: {_py(x, indent + 4, width)}" for k, x in v.items()]
        return _wrap("{", items, "}", indent, width)
    if isinstance(v, (list, tuple)):
        items = [_py(x, indent + 4, width) for x in v]
        if isinstance(v, tuple):
            return _wrap("(", items, ",)" if len(items) == 1 else ")",
                         indent, width)
        return _wrap("[", items, "]", indent, width)
    if isinstance(v, (set, frozenset)):
        if not v:
            return "set()"
        return _wrap("{", sorted(_py(x, indent + 4, width) for x in v), "}",
                     indent, width)
    raise _Opaque(type(v).__name__)


def _wrap(open_, items, close, indent, width) -> str:
    flat = open_ + ", ".join(items) + close
    if len(flat) + indent <= width and "\n" not in flat:
        return flat
    pad = " " * (indent + 4)
    return (open_ + "\n" + "".join(f"{pad}{x},\n" for x in items)
            + " " * indent + close)


def _shown_graph(text: str) -> str:
    """A fixture as a participant sees it: without its comment lines, which
    explain what the test is designed to catch — that is, the answer."""
    lines = [line for line in text.splitlines()
             if not line.lstrip().startswith("#")]
    while lines and not lines[0].strip():
        lines.pop(0)
    return "\n".join(lines).rstrip() + "\n"


def _inputs(ex_dir) -> dict:
    """What a participant needs besides the code to answer: how the region is
    called, and the graph it is given — the very call the answers were
    derived from (the driver's first case).

    Returns ``{"call", "input_graph", "inputs_shown", "inputs_missing"}``.
    ``inputs_shown`` is ``"complete"`` when every argument could be written
    back as Python source; otherwise the reason is in ``inputs_missing`` and
    the reviewer has to describe the input by hand. A region called through
    its ``demo()`` harness is shown with that harness, which builds the
    inputs: it is the same text on both sides.
    """
    import inspect
    from .harness import fixture_graph
    ex_dir = Path(ex_dir).resolve()
    out = {"call": None, "input_graph": None, "inputs_shown": "none",
           "inputs_missing": None}
    spec = _driver_spec(ex_dir) or {}
    entry = spec.get("entry")
    cases = _call_cases(ex_dir, spec)
    if not spec:
        out["inputs_missing"] = "the driver could not be read back"
        return out
    if not entry or not cases:
        out["inputs_missing"] = "no call case in the driver (module-level " \
                                "region or custom driver)"
        return out
    py_path = ex_dir / "original.py"
    ns: dict = {"__name__": "__task__", "__file__": str(py_path)}
    try:
        with _in_example(ex_dir), contextlib.redirect_stdout(io.StringIO()):
            exec(compile(py_path.read_text(), str(py_path), "exec"), ns)
            case = cases[0]
            args, kw = case() if callable(case) else case
        fn = ns[entry]
        try:
            bound = inspect.signature(fn).bind(*args, **kw).arguments
            named = [(k, v) for k, v in bound.items()]
        except (TypeError, ValueError):
            named = [(None, v) for v in args] + list(kw.items())
        graphs = [v for _, v in named if _is_graph(v) and len(v)]
        # a data file of the example passed by path: the participant sees
        # its name and, for an RDF file, its content as the input graph
        files = [Path(v) for _, v in named if isinstance(v, str)
                 and Path(v).is_absolute() and Path(v).is_file()
                 and Path(v).resolve().is_relative_to(ex_dir)]
        if len(graphs) + len(files) > 1:
            raise _Opaque("several input graphs or files")
        rendered = []
        for k, v in named:
            if _is_graph(v):
                text = "g" if len(v) else "Graph()"
            elif files and v == str(files[0]):
                text = repr(files[0].name)
            else:
                text = _py(v, 4)
            rendered.append(f"{k}={text}" if k else text)
    except _Opaque as exc:
        out["inputs_missing"] = f"an argument cannot be shown as source: {exc}"
        return out
    except Exception as exc:
        out["inputs_missing"] = f"the call case does not run in-process: " \
                                f"{type(exc).__name__}"
        return out
    call = _wrap(f"{entry}(", rendered, ")", 0, 72)
    if graphs:
        fixture = spec.get("fixture")
        g = graphs[0]
        if fixture and (ex_dir / fixture).exists() \
                and len(fixture_graph(ex_dir / fixture)) == len(g):
            out["input_graph"] = _shown_graph((ex_dir / fixture).read_text())
        else:
            out["input_graph"] = g.serialize(format="turtle")
        call = "# g is the input graph shown above\n" + call
    if files:
        out["input_graph"] = _shown_graph(files[0].read_text())
        call = (f"# {files[0].name} contains the input graph shown above\n"
                + call)
    if entry == "demo":
        text = py_path.read_text()
        start = text.index("def demo(")
        call = text[start:].rstrip() + "\n\n\n" + call
    out["call"] = call + "\n"
    out["inputs_shown"] = "complete"
    return out


_PROVENANCE_HEADER = ("# Extracted from ", "# region: ",
                      "# licence of the source repository")
_SHIM_COMMENT = re.compile(r"\s*#\s*context shim\b.*$")


def display_source(text: str) -> str:
    """What a participant is shown of one artefact: the region, not the study.

    Both files of a pair carry scaffolding that belongs to the validation,
    not to the code under study: a provenance header, a `# context shim`
    remark on the imports the extraction had to restore, and, for 61 of the
    350 pairs, a `demo()` harness appended identically to both sides. A
    reader timed on the program should not read them. The cut is the same
    on both sides, so it cannot favour either notation: the header lines at
    the top, the shim remarks, and everything from the comment block that
    introduces a top-level `def demo(` to the end of the file.
    """
    lines = text.splitlines()
    while lines and lines[0].startswith(_PROVENANCE_HEADER):
        lines.pop(0)
    demo = next((i for i, line in enumerate(lines)
                 if line.startswith("def demo(")), None)
    if demo is not None:
        cut = demo
        while cut > 0 and (lines[cut - 1].startswith("#")
                           or not lines[cut - 1].strip()):
            cut -= 1
        lines = lines[:cut]
    lines = [_SHIM_COMMENT.sub("", line) for line in lines]
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    return "\n".join(lines) + "\n"


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


def _draft_questions(triples, value, rng: random.Random,
                     removed=None) -> list[dict]:
    """Draft prompts, chosen by what the region actually shows."""
    qs: list[dict] = []
    if removed and not triples:
        qs.append({
            "type": "count",
            "prompt_draft": "How many RDF triples does this code remove from "
                            "the input graph?",
            "answer": len(removed),
        })
        s, p, o = rng.choice(removed)
        qs.append({
            "type": "triple-membership",
            "prompt_draft": "Is the triple "
                            f"{s} {p} {o} still in the graph afterwards?",
            "answer": False,
        })
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
    rng = random.Random(config["strata"]["seed"])
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
        triples, value, removed = _observables(ex_dir, meta)
        fixture = (_driver_spec(ex_dir) or {}).get("fixture")
        inputs = _inputs(ex_dir)
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
                "rdflib": display_source((ex_dir / "original.py").read_text()),
                "ldpy": display_source(
                    (ex_dir / "translated.ldpy").read_text()),
            },
            "derived_triples": triples,
            "derived_removed": removed,
            "derived_value": value,
            # what could be derived automatically. "none" means the region
            # could not be exercised in-process — it needs context the
            # example directory does not carry (a network service, a
            # database, a package of its own repository). Its comprehension
            # questions have to be written by hand before the task is
            # usable; the review step is where that happens.
            "derivation": ("triples" if triples else "removed" if removed
                           else "value" if value is not None else "none"),
            "questions_draft": _draft_questions(triples, value, rng, removed),
            # the call the answers were derived from, and the graph it is
            # given: without them a question about this region's output has
            # no answer the participant can find
            **inputs,
            "review_status": "draft",
        }
        if reads and fixture and (ex_dir / fixture).exists() \
                and not task["input_graph"]:
            # a reading task is unanswerable without the graph it reads
            task["input_graph"] = _shown_graph((ex_dir / fixture).read_text())
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
    shown = sum(1 for t in tasks if t["inputs_shown"] == "complete")
    print("userstudy: %d of %d show the call their answers come from; the "
          "other %d need their input described by hand at review"
          % (shown, len(tasks), len(tasks) - shown))
    print("userstudy: %d of %d carry automatically derived facts; the other "
          "%d need their questions written by hand at review"
          % (derived, len(tasks), len(tasks) - derived))
