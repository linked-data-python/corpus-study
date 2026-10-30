"""Validation driver for hidden-graph__rdflib-starlight__tests_unit_test_result_patches.py__TestSelectStarOverGroundPatternIteration_test_matching_fact_agrees_with_ask.

The region is a test: it returns None and its whole content is one
`assert <ASK answer> is True` over the graph that `_graph_with_one_fact()`
returns.  With a single graph (the one-fact graph) the pair could only prove
"does not raise": an ASK weakened to `{ <a> <b> ?x }`, or replaced by `ask =
True`, stayed green.  The observable of a test is *whether it raises*, so this
driver varies the graph the test is run on and compares, on both sides, the
outcome of the call (None, or the exception, by type and message).

It cannot be written with run_pair's `calls=`, which has no way to hand the
test a different graph: the graph comes from the module-level name
`_graph_with_one_fact` that the region imports from the shim.  The driver
executes both artefacts itself, and, for each graph below, rebinds that name
in the namespace of each side before calling the test (the test resolves it at
call time).  The graphs are built as the shim builds its own, by parsing
N-Triples (`g.parse(data=..., format="nt")`), the input type the repository
uses.

The ASK is `ASK { <a> <b> <c> . }`.  Cases, with the outcome expected from the
original (all verified by running the original):

  - the target fact alone, and with unrelated triples around it: returns None;
  - the empty graph: AssertionError;
  - for each of the three terms of the pattern, a graph whose only triple
    shares the OTHER TWO terms with the target -- other object (a b d), other
    predicate (a x c), other subject (z b c): AssertionError.  A pattern whose
    subject, predicate or object was widened to a variable answers True on
    the matching one of them (each of the three widenings, and `ask = True`, fails this driver on a copy);
  - the three neighbours AND the target in one graph: returns None (a wrong
    answer cannot come from the neighbours);
  - the same three terms in other roles (c b a, b a c): AssertionError;
  - an object that is the plain literal `"<http://example/c>"`
    (the near-miss that the translation notes describe: a str spliced as a
    literal instead of an IRI): AssertionError;
  - the reflexive fact (a a a), no match for (a b c): AssertionError.
"""
import json
import sys
from pathlib import Path

from rdflib import Graph

from rdfeval import harness

NT = "<http://example/{}>"


def _nt(*triples):
    lines = []
    for s, p, o in triples:
        obj = f'"{NT.format(o[1:])}"' if o.startswith("'") else NT.format(o)
        lines.append(f"{NT.format(s)} {NT.format(p)} {obj} .")
    g = Graph()
    g.parse(data="\n".join(lines), format="nt")
    return g


TARGET = ("a", "b", "c")
CASES = {
    "target alone": [TARGET],
    "empty graph": [],
    "target among unrelated triples": [TARGET, ("x", "y", "z"), ("c", "b", "a")],
    "other object (a b d)": [("a", "b", "d")],
    "other predicate (a x c)": [("a", "x", "c")],
    "other subject (z b c)": [("z", "b", "c")],
    "three neighbours, no target": [("a", "b", "d"), ("a", "x", "c"),
                                    ("z", "b", "c")],
    "target and its three neighbours": [("a", "b", "d"), ("a", "x", "c"),
                                        ("z", "b", "c"), TARGET],
    "terms in other roles (c b a)": [("c", "b", "a")],
    "terms in other roles (b a c)": [("b", "a", "c")],
    "reflexive fact (a a a)": [("a", "a", "a")],
    "literal object spelled like the IRI": [("a", "b", "'c")],
}

ex_dir = Path(__file__).resolve().parent
verdict: dict = {"example": ex_dir.name, "equivalent": False,
                 "method": "entry:test_matching_fact_agrees_with_ask "
                           "(custom: outcome over several graphs)",
                 "diffs": [], "error": None}
try:
    ns_o, _ = harness._exec_python(ex_dir / "original.py")
    ns_t, _ = harness._exec_ldpy(ex_dir / "translated.ldpy")
    diffs = []
    outcomes = {}
    for label, triples in CASES.items():
        results = []
        for ns in (ns_o, ns_t):
            ns["_graph_with_one_fact"] = lambda t=triples: _nt(*t)
            results.append(harness._outcome(
                ns["test_matching_fact_agrees_with_ask"], (None,), {}))
        ro, rt = results
        outcomes[label] = repr(ro)
        if ro != rt:
            diffs.append(f"{label}: outcome differs ({ro!r} vs {rt!r})")
    # the cases must actually discriminate: some raise, some do not
    kinds = {v == "None" for v in outcomes.values()}
    if kinds != {True, False}:
        diffs.append(f"the cases do not discriminate: {outcomes}")
    verdict["outcomes"] = outcomes
    verdict["diffs"] = diffs
    verdict["equivalent"] = not diffs
except Exception:
    import traceback
    verdict["error"] = traceback.format_exc(limit=8)

harness._emit(verdict)
VERDICT = verdict
