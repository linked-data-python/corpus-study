"""Validation driver for pyscal__atomRDF__atomrdf_datamodels_defects_grainboundary.py__GrainBoundary_from_graph.

This region READS a graph, so the oracle is not isomorphism but the equality
of the values both versions produce from the same input graph (design record
corpus/405).  Each fixture is parsed fresh for each side and each call.

`demo(graph, sample)` (identical on both sides, appended after the extracted
region -- see meta.json) calls `GrainBoundary.from_graph` through the
ordinary classmethod protocol and returns a plain dict (a pydantic model
instance would compare unequal across the two sides' distinct classes).

ISOLATION PER SIDE.  Both artefacts attach their own `from_graph` to the
shim's GrainBoundary class (`GrainBoundary.from_graph = classmethod(...)`).
The shim is cached in `sys.modules`, so with a single import both sides
patched ONE class and both `demo()`s ran the LAST region executed -- the
translation compared with itself (the triage showed an original.py whose
body was replaced by `return None` staying green).  This driver drops
`atomrdf_context` from `sys.modules` before each side, so each side imports
its own shim and its own class, and it CHECKS that the isolation holds:
the two GrainBoundary classes are distinct, and each class's `from_graph`
wraps the function its own artefact defined.

What every call observes: the returned value (model_dump, or None) or the
exception (type and message), the warnings, what is printed on stdout and
stderr, and the input graph after the call (the region only reads: it must
leave the graph isomorphic to the other side's).

The calls -- the material node decides the defect pattern, the defect node
decides the rdf:type read:

  fixture.ttl
    ex:sample1      two defects: a TwistGrainBoundary neighbour, then a full
                    GrainBoundary (the original call, kept)
    ex:sample2      a defect, none a GrainBoundary: zero solutions through a
                    non-empty loop (the original call, kept)
    ex:sample3      absent from the graph: material None -> the original's
                    `graph.triples((None, …))` is a WILDCARD over every
                    material.  Reached by the repository: a sample with an
                    rdf:type and no cmso:hasMaterial
                    (atomrdf/datamodels/structure.py:818-862)
    ex:sample-typed-only  the same, with the sample really present
    ex:sample4      a material with no defect: the loop never runs
    ex:sample5      two GrainBoundaries on one material: the first one wins
    ex:sample6/7    a defect with two rdf:type values, in both orders
    ex:sample8      an untyped defect (typev None) before a GrainBoundary
    ex:sample9      neighbours only: another predicate, a literal type, a
                    defect of the sample instead of its material
    ex:sample10/11  falsy material literals "" and "0" (not wildcards)
    None            sample None: get_material's own value() is a wildcard
    "http://example.org/sample1"  a str sample (get_material coerces it;
                    the repository passes URIRefs, see get_sample_object)
  fixture_nogb.ttl
    ex:lonely       material None in a graph whose only defect is a twist
  empty graph
    ex:sample1      material None and nothing to read
"""
import contextlib
import io
import sys
import traceback
import warnings
from pathlib import Path

from rdflib import Graph, Namespace

from rdfeval.harness import (Raised, _compare_value, _emit, _exec_ldpy,
                             _exec_python, fixture_graph)

HERE = Path(__file__).resolve().parent
FIXTURE = HERE / "fixture.ttl"
FIXTURE_NOGB = HERE / "fixture_nogb.ttl"
SHIM = "atomrdf_context"
EX = Namespace("http://example.org/")

CASES = [(FIXTURE, EX[s]) for s in (
    "sample1", "sample2", "sample3", "sample-typed-only", "sample4", "sample5",
    "sample6", "sample7", "sample8", "sample9", "sample10", "sample11")]
CASES += [(FIXTURE, None), (FIXTURE, "http://example.org/sample1"),
          (FIXTURE_NOGB, EX.lonely), (None, EX.sample1)]


def graph_for(path):
    return Graph() if path is None else fixture_graph(path)


def observe(fn, graph, sample):
    out, err = io.StringIO(), io.StringIO()
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                result = fn(graph, sample)
            except Exception as e:  # noqa: BLE001 -- the exception IS the observation
                result = Raised(e)
    return {"result": result,
            "warnings": [(w.category.__name__, str(w.message)) for w in caught],
            "stdout": out.getvalue(), "stderr": err.getvalue()}


def run_side(execute, path, name):
    """Execute one artefact against its OWN copy of the shim module."""
    sys.modules.pop(SHIM, None)
    ns, out = execute(path, name)
    sys.modules.pop(SHIM, None)
    return ns, out


def main() -> dict:
    verdict: dict = {"example": HERE.name, "equivalent": False,
                     "method": "custom:fixture-values, shim isolated per side",
                     "diffs": [], "error": None}
    try:
        ns_o, out_o = run_side(_exec_python, HERE / "original.py", "__original__")
        ns_t, out_t = run_side(_exec_ldpy, HERE / "translated.ldpy", "__translated__")
    except Exception:
        verdict["error"] = traceback.format_exc(limit=8)
        _emit(verdict)
        return verdict

    diffs: list[str] = []
    # the isolation must hold, or the pair compares one region with itself
    cls_o, cls_t = ns_o.get("GrainBoundary"), ns_t.get("GrainBoundary")
    if cls_o is None or cls_t is None or cls_o is cls_t:
        diffs.append("isolation broken: both sides share one GrainBoundary class")
    for label, ns, cls in (("original", ns_o, cls_o), ("translated", ns_t, cls_t)):
        fn = getattr(ns.get("from_graph"), "__func__", None)
        attached = getattr(getattr(cls, "from_graph", None), "__func__", None)
        if fn is None or attached is not fn:
            diffs.append(f"isolation broken: {label} GrainBoundary.from_graph "
                         "is not the region of that side")

    found = 0
    for i, (path, sample) in enumerate(CASES):
        label = f"call[{i}] {getattr(path, 'name', 'empty graph')} {sample!r}"
        g_o, g_t = graph_for(path), graph_for(path)
        ro, rt = observe(ns_o["demo"], g_o, sample), observe(ns_t["demo"], g_t, sample)
        if isinstance(ro["result"], Raised) or isinstance(rt["result"], Raised):
            if ro["result"] != rt["result"]:
                diffs.append(f"{label}: outcome differs ({ro['result']!r} vs {rt['result']!r})")
        else:
            _compare_value(ro["result"], rt["result"], f"{label}.result", diffs)
            found += ro["result"] is not None
        for key in ("warnings", "stdout", "stderr"):
            if ro[key] != rt[key]:
                diffs.append(f"{label}: {key} differs ({ro[key]!r} vs {rt[key]!r})")
        _compare_value(g_o, g_t, f"{label}.graph", diffs)
    # the fixture must really reach both outcomes
    if not 0 < found < len(CASES):
        diffs.append(f"driver reached {found} GrainBoundary results out of {len(CASES)}")
    if out_o != out_t:
        diffs.append("stdout differs at module level")

    verdict["calls"] = len(CASES)
    verdict["found"] = found
    verdict["diffs"] = diffs
    verdict["equivalent"] = not diffs
    _emit(verdict)
    return verdict


VERDICT = main()
