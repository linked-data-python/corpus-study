"""Validation driver for hidden-graph__rdflib-starlight__tests_unit_test_result_patches.py__TestSelectStarOverGroundPatternIteration_test_nonmatching_fact_yields_zero_rows.

Establishes semantic equivalence of original.py and translated.ldpy.

The region is a bound test method whose body never uses `self` (a plain
`None` stands in for it): it builds its graph with `_graph_with_one_fact()`,
runs one ground SELECT * and asserts. Its only observable outcome is whether
it returns or which `assert` fails -- and those asserts carry no message, so
two failing runs raise identical `AssertionError()`s. This driver therefore
records, for a failing run, the source text of the assert that failed.

One fact (a b c) and one zero-row query prove only the object IRI: widening
the subject or predicate to a variable, or changing the subject to another
constant, left the first driver green. The seam is the graph-building
helper, NOT the region: after executing each side, `_graph_with_one_fact` in
that side's globals is replaced by a factory building the case's graph
(the repository's helper itself is kept as the first case). Cases, each
built fresh for each side:

  ``repo-helper``  the repository's own helper (a b c): zero rows, the test
                   passes.
  ``empty``        no triple at all: zero rows, passes.
  ``neighbours``   a b c, x b nope, a y nope -- each shares two of the three
                   pattern terms: still zero rows, passes; a pattern whose
                   subject, predicate or object is widened to a variable
                   would match one of them.
  ``match``        a b nope beside a b c: the pattern matches once with zero
                   variables bound, and the test FAILS -- at
                   ``r.bindings == []`` under plain rdflib, whose
                   ``Result.__iter__`` drops the empty row; at
                   ``list(r) == []`` once starlight's patch is in place.  A
                   changed constant (subject, predicate or object) would
                   make it pass instead.

Every case runs twice: under plain rdflib, then with starlight's import-time
patch of ``rdflib.query.Result.__iter__`` (the real test module does
``import starlight``, tests/unit/test_result_patches.py:7; the extraction
does not). The patch is global, so it is applied once for both sides, and
removed afterwards.
"""
import importlib.util
import json
import sys
import traceback
from pathlib import Path

from rdflib import Graph
from rdflib.query import Result

from rdfeval import harness

ENTRY = "test_nonmatching_fact_yields_zero_rows"
ex_dir = Path(__file__).resolve().parent

A, B, C, NOPE = ("<http://example/a>", "<http://example/b>",
                 "<http://example/c>", "<http://example/nope>")
X, Y = "<http://example/x>", "<http://example/y>"
CASES = {
    "repo-helper": None,
    "empty": "",
    "neighbours": f"{A} {B} {C} .\n{X} {B} {NOPE} .\n{A} {Y} {NOPE} .\n",
    "match": f"{A} {B} {C} .\n{A} {B} {NOPE} .\n",
}


def _factory(repo_helper, nt):
    if nt is None:
        return repo_helper

    def build() -> Graph:
        g = Graph()
        g.parse(data=nt, format="nt")
        return g
    return build


def _source_line(fn_file: Path):
    """Generated line number -> source line number of the executed artefact.

    A ``.ldpy`` runs as its transpiled code, which starts with a runtime
    import line of its own: the transpiler's language map gives back the
    ``.ldpy`` line a traceback line comes from.
    """
    if fn_file.suffix != ".ldpy":
        return lambda n: n
    from ldpy.transpiler import transpile
    lmap = transpile(fn_file.read_text(), filename=str(fn_file)).map
    return lmap.src_line_for_gen_line


def _outcome(ns, fn_file):
    """('returned', value) or ('raised', type, message, failing source line)."""
    try:
        return ("returned", ns[ENTRY](None))
    except Exception as e:                      # noqa: BLE001 - compared
        line = None
        to_src = _source_line(fn_file)
        for frame, lineno in traceback.walk_tb(e.__traceback__):
            if frame.f_code.co_name == ENTRY:
                line = fn_file.read_text().splitlines()[to_src(lineno) - 1].strip()
        return ("raised", type(e).__name__, str(e), line)


verdict: dict = {"example": ex_dir.name, "equivalent": False,
                 "method": f"entry:{ENTRY} (graph seam, failing assert, "
                           "plain and starlight-patched Result.__iter__)",
                 "diffs": [], "error": None}
original_iter = Result.__iter__
try:
    left, right = harness.sides_from_env()
    ns_o, out_o = harness._exec_python(ex_dir / "original.py")
    ns_t, out_t = harness._exec_ldpy(ex_dir / "translated.ldpy")
    repo_helper = ns_o["_graph_with_one_fact"]
    diffs, outcomes = [], {}
    if out_o != out_t:
        diffs.append("module-level stdout differs")
    for mode in ("plain", "starlight"):
        if mode == "starlight":
            spec = importlib.util.spec_from_file_location(
                "starlight_result_patches", ex_dir / "starlight_result_patches.py")
            patches = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(patches)
            if not patches.patch_result_iter_empty_binding_row():
                raise RuntimeError("starlight's Result.__iter__ patch did not apply")
        for case, nt in CASES.items():
            ns_o["_graph_with_one_fact"] = _factory(repo_helper, nt)
            ns_t["_graph_with_one_fact"] = _factory(repo_helper, nt)
            ro = _outcome(ns_o, ex_dir / left)
            rt = _outcome(ns_t, ex_dir / right)
            outcomes[f"{mode}/{case}"] = list(ro)
            if ro != rt:
                diffs.append(f"{mode}/{case}: outcome differs ({ro!r} vs {rt!r})")
    verdict["outcomes"] = outcomes
    verdict["calls"] = len(outcomes) * 2
    verdict["diffs"] = diffs
    verdict["equivalent"] = not diffs
except Exception:
    verdict["error"] = traceback.format_exc(limit=8)
finally:
    Result.__iter__ = original_iter

harness._emit(verdict)
VERDICT = verdict
