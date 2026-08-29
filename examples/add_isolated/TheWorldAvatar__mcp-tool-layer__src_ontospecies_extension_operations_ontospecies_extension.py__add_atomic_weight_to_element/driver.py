"""Validation driver for TheWorldAvatar__mcp-tool-layer__src_ontospecies_extension_operations_ontospecies_extension.py__add_atomic_weight_to_element.

add_atomic_weight_to_element opens its graph through `with locked_graph() as
g:` and returns only a plain string (str(aw), or an error message) -- never
the graph itself, which is also not one of its own parameters. run_pair's
built-in entry=/calls= comparison only ever looks at a function's RETURN
VALUE and its own positional/keyword ARGUMENTS, so it cannot see what got
written to `g`: comparing just the returned string would be exactly the
"hollow green" INSTRUCTIONS_403 SS5 warns about, since the string (built from
a deterministic stand-in `aw`, see context_shim.py) is identical whether or
not the tail g.add()->+{ }(g) site under test actually ran.

So, following the precedent set by add_isolated/BBDFrancois.../driver.py
(also bypassing run_pair's call loop for a region whose real state does not
travel through a return value or an argument), this driver drives both sides
by hand: call the "original" fully, snapshot the graph context_shim.
locked_graph handed it (context_shim.LAST_GRAPH -- a fresh Graph() per call,
see context_shim.py), THEN call the "translated" version and snapshot ITS
graph, THEN compare the two snapshots by isomorphism. The two calls never
overlap -- call, snapshot, reset, call, snapshot -- so there is no race on
the shared context_shim.LAST_GRAPH slot (module imports are cached, so both
sides' `from context_shim import locked_graph` resolve to the same module
object; see also the sibling note in ..._write_integrated_ttl/meta.json
about NOT sharing a mutable object between the two sides this way).

Four cases exercise every path through the region:
  * a normal numeric value (float-datatype branch, reaches the tail +{ });
  * the literal string "N/A" (the other branch of value == "N/A");
  * a value that fails float() (early return INSIDE the try/except, before
    the tail +{ } -- proves the pair does NOT add a spurious triple there);
  * a non-absolute element_iri (earliest return, before the graph is
    touched at all).
"""
from __future__ import annotations

import traceback
from pathlib import Path

from rdflib import Graph

from rdfeval.harness import _exec_ldpy, _exec_python, _emit, graphs_isomorphic

import context_shim

HERE = Path(__file__).resolve().parent

CASES = [
    ("https://example.org/element/O", 15.999),
    ("https://example.org/element/He", "N/A"),
    ("https://example.org/element/Xx", "not-a-number"),
    ("not-an-absolute-iri", 1.0),
]

verdict = {"example": HERE.name, "equivalent": False,
           "method": "entry:add_atomic_weight_to_element",
           "diffs": [], "error": None}

try:
    ns_o, out_o = _exec_python(HERE / "original.py")
    ns_t, out_t = _exec_ldpy(HERE / "translated.ldpy")
    fo = ns_o.get("add_atomic_weight_to_element")
    ft = ns_t.get("add_atomic_weight_to_element")
    if not callable(fo) or not callable(ft):
        raise RuntimeError("entry point not found in both modules")

    diffs: list[str] = []
    for i, (element_iri, value) in enumerate(CASES):
        context_shim.LAST_GRAPH = None
        ro = fo(element_iri, value)
        go = context_shim.LAST_GRAPH or Graph()

        context_shim.LAST_GRAPH = None
        rt = ft(element_iri, value)
        gt = context_shim.LAST_GRAPH or Graph()

        if ro != rt:
            diffs.append(f"case[{i}]: result differs ({ro!r} vs {rt!r})")
        if not graphs_isomorphic(go, gt):
            diffs.append(f"case[{i}]: graphs not isomorphic "
                         f"({len(go)} vs {len(gt)} triples)")

    if out_o != out_t:
        diffs.append(f"stdout differs ({out_o[:200]!r} vs {out_t[:200]!r})")

    verdict["diffs"] = diffs
    verdict["equivalent"] = not diffs
except Exception:
    verdict["error"] = traceback.format_exc(limit=8)

_emit(verdict)
VERDICT = verdict
