"""Execution/comparison helpers used by example validation drivers.

A driver calls :func:`run_pair`, which

  1. executes ``original.py`` and ``translated.ldpy`` (through the ldpy
     transpiler) in two fresh module namespaces, capturing stdout;
  2. either compares *module state* (every rdflib Graph in the globals,
     paired by variable name, plus non-graph variables both modules define),
     or — when ``entry`` names a function — calls it with each fixture in
     ``calls`` and compares the results;
  3. graph comparison is rdflib graph isomorphism (``rdflib.compare``),
     never raw serialisation; other values are normalised
     (term-by-term for lists/tuples/sets/dicts) then compared for equality.

**Reading regions** (the oracle of design record ``corpus/403``) are not
covered by graph isomorphism: they produce *values*, so the oracle is the
equality of what the two versions produce from the same input graph.  Pass
``fixture=`` a Turtle file and :func:`run_pair` parses it into a fresh graph
per side and calls the entry point with it.  Two properties of RDF reading
shape the comparison:

  * a lazy result — a generator, an rdflib ``Result``, an ldpy match — is
    **materialised** before anything is compared, on both sides;
  * the order in which a store yields solutions is not specified, so results
    are compared as **multisets** unless ``ordered=True`` says the region
    itself imposes an order (it sorts, or the query has an ``ORDER BY``).

The verdict is a JSON-serialisable dict; drivers print it so the validate
stage can collect it from a subprocess.
"""

from __future__ import annotations

import contextlib
import io
import json
import sys
import traceback
from pathlib import Path


def _exec_python(path: Path) -> tuple[dict, str]:
    ns: dict = {"__name__": "__original__", "__file__": str(path)}
    out = io.StringIO()
    code = compile(path.read_text(), str(path), "exec")
    with contextlib.redirect_stdout(out):
        exec(code, ns)
    return ns, out.getvalue()


def _exec_ldpy(path: Path) -> tuple[dict, str]:
    from ldpy.transpiler import transpile
    r = transpile(path.read_text(), filename=str(path))
    ns: dict = {"__name__": "__translated__", "__file__": str(path)}
    out = io.StringIO()
    code = compile(r.code, str(path), "exec")
    with contextlib.redirect_stdout(out):
        exec(code, ns)
    return ns, out.getvalue()


def fixture_graph(path) -> object:
    """A fresh graph parsed from a Turtle fixture.

    Called once per side, so a region that also *writes* cannot leak its
    effects into the other version's input.
    """
    from rdflib import Graph
    p = Path(path)
    return Graph().parse(source=str(p), format="turtle")


_ATOMIC = (str, bytes, bytearray, dict, set, frozenset, list, tuple)


def materialise(value):
    """Walk a lazy result until it is comparable.

    ``g.objects(...)`` is a generator, ``g.query(...)`` an rdflib ``Result``,
    ``m{ }`` a lazy match: none of them compares as a value, and each is
    consumed by being read.  Everything iterable that is not already a
    container, a string or a graph becomes a list; rows become tuples.
    """
    from rdflib import Graph
    from rdflib.query import Result, ResultRow
    if isinstance(value, Result):
        if value.type == "ASK":
            return bool(value)
        return [materialise(row) for row in value]
    if isinstance(value, ResultRow):
        return tuple(value)
    if isinstance(value, (Graph, str, bytes, bytearray)):
        return value
    if isinstance(value, dict):
        return {k: materialise(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return type(value)(materialise(v) for v in value)
    if isinstance(value, (set, frozenset)):
        return {materialise(v) for v in value}
    if hasattr(value, "__iter__") and not isinstance(value, _ATOMIC):
        return [materialise(v) for v in value]
    return value


def _multiset(value):
    """A comparison key that ignores order but not multiplicity."""
    return sorted(repr(normalise(v)) for v in value)


def _graphs(ns: dict) -> dict[str, object]:
    from rdflib import Graph
    return {k: v for k, v in ns.items()
            if isinstance(v, Graph) and not k.startswith("_")}


def graphs_isomorphic(g1, g2) -> bool:
    from rdflib.compare import to_isomorphic
    return to_isomorphic(g1) == to_isomorphic(g2)


def normalise(value):
    """Make values comparable across the two runs (BNode ids differ)."""
    from rdflib import BNode, Graph
    if isinstance(value, Graph):
        from rdflib.compare import to_isomorphic
        return ("graph", to_isomorphic(value).graph_digest())
    if isinstance(value, BNode):
        return ("bnode",)
    if isinstance(value, dict):
        return {k: normalise(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [normalise(v) for v in value]
    if isinstance(value, set):
        return sorted(map(repr, (normalise(v) for v in value)))
    return value


def _compare_value(a, b, label: str, diffs: list[str],
                   ordered: bool = True) -> None:
    from rdflib import Graph
    if isinstance(a, Graph) and isinstance(b, Graph):
        if not graphs_isomorphic(a, b):
            diffs.append(f"{label}: graphs not isomorphic "
                         f"({len(a)} vs {len(b)} triples)")
        return
    try:
        a, b = materialise(a), materialise(b)
        if not ordered and isinstance(a, (list, tuple)) \
                and isinstance(b, (list, tuple)):
            equal = _multiset(a) == _multiset(b)
        else:
            equal = normalise(a) == normalise(b)
    except Exception as e:
        diffs.append(f"{label}: comparison error {e}")
        return
    if not equal:
        diffs.append(f"{label}: values differ ({a!r} vs {b!r})")


def run_pair(driver_file: str, entry: str | None = None,
             calls: list | None = None, fixture: str | None = None,
             ordered: bool | None = None) -> dict:
    """Establish that ``original.py`` and ``translated.ldpy`` agree.

    ``entry``/``calls``   compare what a function returns and what it mutates
    ``fixture``           a Turtle file, parsed fresh for each side and passed
                          to ``entry`` as its single argument — the reading
                          oracle: same input graph, same values out
    ``ordered``           whether the order of a sequence is part of the
                          region's meaning.  Defaults to True, and to False
                          for a fixture run: no RDF store promises an order,
                          so a region that wants one must sort or ``ORDER BY``
                          — and then the driver says ``ordered=True``.
    """
    ex_dir = Path(driver_file).resolve().parent
    if ordered is None:
        ordered = fixture is None
    verdict: dict = {"example": ex_dir.name, "equivalent": False,
                     "method": None, "diffs": [], "error": None}
    if fixture is not None:
        if not entry:
            verdict["error"] = "fixture= needs entry= (the region to call)"
            _emit(verdict)
            return verdict
        path = ex_dir / fixture
        if calls is None:
            calls = [lambda: ((fixture_graph(path),), {})]
    try:
        ns_o, out_o = _exec_python(ex_dir / "original.py")
        ns_t, out_t = _exec_ldpy(ex_dir / "translated.ldpy")
    except Exception:
        verdict["error"] = traceback.format_exc(limit=8)
        _emit(verdict)
        return verdict

    diffs: list[str] = []
    if entry:
        verdict["method"] = (f"fixture:{fixture} entry:{entry}"
                             if fixture else f"entry:{entry}")
        verdict["ordered"] = ordered
        fo, ft = ns_o.get(entry), ns_t.get(entry)
        if not callable(fo) or not callable(ft):
            verdict["error"] = f"entry {entry!r} not found in both modules"
            _emit(verdict)
            return verdict
        if not calls:
            verdict["error"] = "no fixtures: provide calls=[(args, kwargs), …]"
            _emit(verdict)
            return verdict
        for i, case in enumerate(calls):
            # a case is (args, kwargs) — or a callable returning that pair,
            # invoked once per side so mutable arguments (graphs!) stay fresh
            try:
                args_o, kw_o = case() if callable(case) else case
                args_t, kw_t = case() if callable(case) else case
                # A region whose whole effect is printing has nothing else to
                # compare: capture what each side writes while it runs.
                buf_o, buf_t = io.StringIO(), io.StringIO()
                with contextlib.redirect_stdout(buf_o):
                    ro = fo(*args_o, **kw_o)
                with contextlib.redirect_stdout(buf_t):
                    rt = ft(*args_t, **kw_t)
            except Exception:
                verdict["error"] = traceback.format_exc(limit=8)
                _emit(verdict)
                return verdict
            _compare_value(ro, rt, f"call[{i}].result", diffs, ordered)
            for j, (ao, at) in enumerate(zip(args_o, args_t)):
                _compare_value(ao, at, f"call[{i}].arg[{j}]", diffs, ordered)
            for k in kw_o:
                _compare_value(kw_o[k], kw_t.get(k), f"call[{i}].kwarg[{k}]",
                               diffs, ordered)
            if buf_o.getvalue() != buf_t.getvalue():
                diffs.append(f"call[{i}]: stdout differs "
                             f"({buf_o.getvalue()[:120]!r} vs "
                             f"{buf_t.getvalue()[:120]!r})")
        verdict["calls"] = len(calls)
        if out_o != out_t:
            diffs.append("stdout differs at module level")
    else:
        verdict["method"] = "module-state"
        go, gt = _graphs(ns_o), _graphs(ns_t)
        if set(go) != set(gt):
            diffs.append(f"graph variables differ: {sorted(go)} vs {sorted(gt)}")
        for name in sorted(set(go) & set(gt)):
            _compare_value(go[name], gt[name], f"graph {name}", diffs)
        if out_o != out_t:
            diffs.append("stdout differs")
        verdict["graphs_compared"] = sorted(set(go) & set(gt))
        if not (go or gt) and out_o == out_t == "":
            diffs.append("nothing observable to compare")
    verdict["diffs"] = diffs
    verdict["equivalent"] = not diffs
    _emit(verdict)
    return verdict


def _emit(verdict: dict) -> None:
    print("RDFEVAL-VERDICT " + json.dumps(verdict), file=sys.stderr)
