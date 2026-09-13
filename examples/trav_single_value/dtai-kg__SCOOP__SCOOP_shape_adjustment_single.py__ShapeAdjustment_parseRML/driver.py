"""Validation driver for dtai-kg__SCOOP__SCOOP_shape_adjustment_single.py__ShapeAdjustment_parseRML.

This region READS a graph, so the oracle is not isomorphism but the equality
of the values both versions produce from the same input graph (design record
corpus/405).  `fixture.ttl` is parsed fresh for each side.

parseRML is a method (`self` is its first parameter) that mutates
`self.rml_parsed` rather than returning anything, and takes `self` and
`rml_graph` -- two positional arguments, so run_pair's built-in
entry=/fixture= (single positional argument) does not fit.  Following the
precedent of findNode's driver.py in the `remove` stratum (same class, same
repository), this hand-rolls the call: a fresh ShapeAdjustmentStub per side
per fixture parse, then compares the resulting `self.rml_parsed` dict by
plain equality (rdflib terms compare by value; no BNode identifiers appear
in the fixture, so no cross-run BNode renumbering to normalise away).
"""
import traceback
from pathlib import Path

from rdfeval.harness import _emit, _exec_ldpy, _exec_python, fixture_graph, normalise

HERE = Path(__file__).resolve().parent
FIXTURE = HERE / "fixture.ttl"

verdict = {"example": HERE.name, "equivalent": False,
           "method": "entry:parseRML (hand-rolled: self.rml_parsed compared "
                     "by value, self has no useful __eq__)",
           "diffs": [], "error": None}

try:
    ns_o, out_o = _exec_python(HERE / "original.py")
    ns_t, out_t = _exec_ldpy(HERE / "translated.ldpy")
    fo = ns_o.get("parseRML")
    ft = ns_t.get("parseRML")
    Stub_o = ns_o.get("ShapeAdjustmentStub")
    Stub_t = ns_t.get("ShapeAdjustmentStub")
    if not callable(fo) or not callable(ft):
        raise RuntimeError("entry point not found in both modules")
    if Stub_o is None or Stub_t is None:
        raise RuntimeError("ShapeAdjustmentStub not found in both modules")

    diffs: list[str] = []

    self_o = Stub_o()
    self_t = Stub_t()
    fo(self_o, fixture_graph(FIXTURE))
    ft(self_t, fixture_graph(FIXTURE))

    if normalise(self_o.rml_parsed) != normalise(self_t.rml_parsed):
        diffs.append(f"rml_parsed differs ({self_o.rml_parsed!r} vs "
                     f"{self_t.rml_parsed!r})")

    if out_o != out_t:
        diffs.append(f"stdout differs ({out_o[:200]!r} vs {out_t[:200]!r})")

    verdict["diffs"] = diffs
    verdict["equivalent"] = not diffs
    verdict["calls"] = 1
except Exception:
    verdict["error"] = traceback.format_exc(limit=8)

_emit(verdict)
VERDICT = verdict
