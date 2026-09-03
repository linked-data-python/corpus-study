"""Validation driver for TheWorldAvatar__mcp-tool-layer__src_ontospecies_extension_operations_ontospecies_extension.py__delete_triple.

delete_triple opens its graph through `with locked_graph() as g:` and
returns only a string -- never the graph itself, which is also not one of
its own parameters (subject_iri, predicate_iri and object_value are plain
strs). run_pair's built-in entry=/calls= comparison only ever looks at a
function's RETURN VALUE and its own ARGUMENTS, so it cannot see whether the
`-{ }` site under test actually removed anything from `g`: two of the four
cases below return the exact same string ("Removed triple (...)") whether or
not the removal happened, since the string is built from s/p/o alone.
Comparing just the returned string would be exactly the "hollow green"
INSTRUCTIONS SS3 warns about.

So, following the precedent set by the sibling region
add_isolated/…__add_atomic_weight_to_element/driver.py (also bypassing
run_pair's call loop for a region whose real state does not travel through a
return value or an argument), this driver drives both sides by hand: seed
context_shim.SEED_GRAPH with the graph delete_triple should find already in
`g`, call one side, snapshot what `context_shim.LAST_GRAPH` holds afterward,
THEN do the same for the other side, THEN compare the two snapshots by
isomorphism plus the two returned strings. The two calls never overlap --
seed, call, snapshot, reset -- seed, call, snapshot -- so there is no race on
the shared context_shim module state (module imports are cached, so both
sides' `from context_shim import locked_graph` resolve to the same module
object).

Four cases walk every path through the region:
  * subject/predicate/object all present as an IRI object -- the triple is
    found and removed;
  * subject/predicate present, object a literal -- found and removed
    (exercises the Literal(object_value) branch);
  * a neighbour that must NOT match: same subject and predicate, a
    different (but still absolute-IRI) object -- proves the pair does not
    remove a triple it was not asked to remove;
  * a non-absolute subject_iri -- the earliest return, before `g` is
    touched at all.
"""
from __future__ import annotations

import traceback
from pathlib import Path

from rdflib import Graph, Literal, URIRef

from rdfeval.harness import _exec_ldpy, _exec_python, _emit, graphs_isomorphic

import context_shim

HERE = Path(__file__).resolve().parent

S1 = URIRef("https://example.org/s1")
S2 = URIRef("https://example.org/s2")
P_LIKES = URIRef("https://example.org/likes")
P_NAME = URIRef("https://example.org/name")
O_IRI = URIRef("https://example.org/o1")
O_ELSEWHERE = URIRef("https://example.org/elsewhere")


def seed() -> Graph:
    g = Graph()
    g.add((S1, P_LIKES, O_IRI))
    g.add((S1, P_NAME, Literal("Alice")))
    g.add((S2, P_LIKES, O_IRI))
    return g


CASES = [
    (str(S1), str(P_LIKES), str(O_IRI)),          # present, IRI object
    (str(S1), str(P_NAME), "Alice"),               # present, literal object
    (str(S1), str(P_LIKES), str(O_ELSEWHERE)),     # absolute IRI, no match
    ("not-an-iri", str(P_LIKES), str(O_IRI)),      # non-absolute subject
]

verdict = {"example": HERE.name, "equivalent": False,
           "method": "entry:delete_triple",
           "diffs": [], "error": None}

try:
    ns_o, out_o = _exec_python(HERE / "original.py")
    ns_t, out_t = _exec_ldpy(HERE / "translated.ldpy")
    fo = ns_o.get("delete_triple")
    ft = ns_t.get("delete_triple")
    if not callable(fo) or not callable(ft):
        raise RuntimeError("entry point not found in both modules")

    diffs: list[str] = []
    for i, args in enumerate(CASES):
        context_shim.SEED_GRAPH = seed()
        context_shim.LAST_GRAPH = None
        ro = fo(*args)
        go = context_shim.LAST_GRAPH if context_shim.LAST_GRAPH is not None else context_shim.SEED_GRAPH

        context_shim.SEED_GRAPH = seed()
        context_shim.LAST_GRAPH = None
        rt = ft(*args)
        gt = context_shim.LAST_GRAPH if context_shim.LAST_GRAPH is not None else context_shim.SEED_GRAPH

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
