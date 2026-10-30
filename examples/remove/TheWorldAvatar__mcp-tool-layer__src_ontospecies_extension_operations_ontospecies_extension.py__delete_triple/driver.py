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

Cases (CASES, 27 of them) walk every path through the region:
  * found and removed: an IRI object, plain-literal objects (including the
    falsy "" and "0", and "None"), for both subjects;
  * a neighbour that must NOT match: same subject and predicate with another
    absolute-IRI object;
  * the guard `not _is_abs_iri(subject) or not _is_abs_iri(predicate)` taken
    by each operand alone (non-absolute subject, non-absolute predicate), by
    both, and with the empty string "" for each;
  * absent triples ("No such triple found"), either absent from the graph
    altogether or a one-triple hole in an otherwise full grid.

The seed (seed(holes)) is the full grid subjects x predicates x objects, so
every target has, for each of its three terms, a neighbour that shares the
other two (same subject+predicate, same subject+object, same
predicate+object).  The grid is completed with literals that resemble the
target: "Alice"@en, "Alice"^^xsd:string, the IRI's text as a plain literal, a
non-absolute URIRef node, "0"^^xsd:integer.  Mutants run in a copy against
this driver (translated.ldpy, one change each) and all failed: the removal
replaced by `pass`; subject, predicate or object of the `-{ }` widened to a
variable; the same three widenings in the `m{ }` guard; the guard forced to
True or False; `or` -> `and`; either operand of the first guard removed;
URIRef and Literal swapped; the literal given datatype xsd:string; a falsy
object replaced by "None" in the Literal; a message built from the wrong
term.  The one mutant that stayed green, `_is_abs_iri(o) and o`, is
equivalent (an absolute IRI is never empty).

The snapshots are compared as triple sets and by isomorphism, and the driver
fails if it observed fewer than 8 removals in all (so it cannot go green on a
region that removes nothing).
"""
from __future__ import annotations

import traceback
from pathlib import Path

from rdflib import Graph, Literal, URIRef
from rdflib.namespace import XSD

from rdfeval.harness import _exec_ldpy, _exec_python, _emit, graphs_isomorphic

import context_shim

HERE = Path(__file__).resolve().parent

S1 = URIRef("https://example.org/s1")
S2 = URIRef("https://example.org/s2")
P_LIKES = URIRef("https://example.org/likes")
P_NAME = URIRef("https://example.org/name")
O_IRI = URIRef("https://example.org/o1")
O_ELSEWHERE = URIRef("https://example.org/elsewhere")

SUBJECTS = [S1, S2]
PREDICATES = [P_LIKES, P_NAME]
OBJECTS = [O_IRI, O_ELSEWHERE, Literal("Alice"), Literal("Bob"),
           Literal(""), Literal("0")]


def seed(holes=()) -> Graph:
    """The full grid subjects x predicates x objects, minus `holes`.

    In the grid every triple has, for each of its three terms, a neighbour
    that shares the OTHER two (same subject and predicate with another
    object, same subject and object with another predicate, same predicate
    and object with another subject).  A removal or an existence test that
    widens one term to a wildcard therefore removes or finds a neighbour, and
    the graph differs.  On top of the grid: the literals that look like the
    target without being it (language-tagged, xsd:string, the IRI's text as
    a literal, a non-absolute IRI node, a typed number)."""
    g = Graph()
    for s in SUBJECTS:
        for p in PREDICATES:
            for o in OBJECTS:
                if (s, p, o) not in holes:
                    g.add((s, p, o))
    g.add((S1, P_NAME, Literal("Alice", lang="en")))
    g.add((S1, P_NAME, Literal("Alice", datatype=XSD.string)))
    g.add((S1, P_LIKES, Literal(str(O_IRI))))        # the IRI's text, as a literal
    g.add((S1, P_LIKES, URIRef("o1")))               # a node whose IRI is not absolute
    g.add((S1, P_NAME, Literal("0", datatype=XSD.integer)))
    g.add((S1, P_NAME, Literal("None")))
    return g


# (arguments, holes): `holes` are grid triples left out of the seed, to make
# the "No such triple found" answer one whose neighbours are all present.
CASES = [
    # present, IRI object (original case)
    ((str(S1), str(P_LIKES), str(O_IRI)), ()),
    # present, literal object (original case)
    ((str(S1), str(P_NAME), "Alice"), ()),
    # absolute IRI, no match (original case)
    ((str(S1), str(P_LIKES), str(O_ELSEWHERE)), ((S1, P_LIKES, O_ELSEWHERE),)),
    # non-absolute subject (original case); the other guard operand next
    (("not-an-iri", str(P_LIKES), str(O_IRI)), ()),
    # non-absolute predicate with an absolute subject: second operand of `or`
    ((str(S1), "likes", str(O_IRI)), ()),
    # both non-absolute; empty strings (falsy) for subject and predicate
    (("x", "y", str(O_IRI)), ()),
    (("", str(P_LIKES), str(O_IRI)), ()),
    ((str(S1), "", str(O_IRI)), ()),
    # second subject
    ((str(S2), str(P_NAME), str(O_ELSEWHERE)), ()),
    # literal objects: falsy "" and "0", a number-looking one, "None"
    ((str(S1), str(P_NAME), ""), ()),
    ((str(S2), str(P_LIKES), "0"), ()),
    ((str(S1), str(P_NAME), "Bob"), ()),
    ((str(S1), str(P_NAME), "None"), ()),
    # "0" (plain) next to "0"^^xsd:integer: only the plain one is the target
    ((str(S1), str(P_NAME), "0"), ()),
    # object not absolute although it looks like a name of a node: a literal
    ((str(S1), str(P_LIKES), "o1"), ()),
    # absent triples whose every neighbour is present (one hole each, per kind)
    ((str(S1), str(P_LIKES), str(O_IRI)), ((S1, P_LIKES, O_IRI),)),
    ((str(S2), str(P_NAME), "Bob"), ((S2, P_NAME, Literal("Bob")),)),
    ((str(S1), str(P_NAME), ""), ((S1, P_NAME, Literal("")),)),
    ((str(S2), str(P_LIKES), "0"), ((S2, P_LIKES, Literal("0")),)),
    # absent: not in the grid at all
    ((str(S1), str(P_LIKES), "https://example.org/never"), ()),
    ((str(S1), "https://example.org/never", str(O_IRI)), ()),
    (("https://example.org/never", str(P_LIKES), str(O_IRI)), ()),
    ((str(S1), str(P_NAME), "Carol"), ()),
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
    removals = 0
    for i, (args, holes) in enumerate(CASES):
        context_shim.SEED_GRAPH = seed(holes)
        context_shim.LAST_GRAPH = None
        ro = fo(*args)
        go = context_shim.LAST_GRAPH if context_shim.LAST_GRAPH is not None else context_shim.SEED_GRAPH

        context_shim.SEED_GRAPH = seed(holes)
        context_shim.LAST_GRAPH = None
        rt = ft(*args)
        gt = context_shim.LAST_GRAPH if context_shim.LAST_GRAPH is not None else context_shim.SEED_GRAPH

        removals += len(seed(holes)) - len(go)
        if ro != rt:
            diffs.append(f"case[{i}]: result differs ({ro!r} vs {rt!r})")
        if set(go) != set(gt) or not graphs_isomorphic(go, gt):
            diffs.append(f"case[{i}]: graphs not isomorphic "
                         f"({len(go)} vs {len(gt)} triples)")

    # the driver must really see removals: at least the 8 cases that find
    # their triple remove exactly one triple each (original side)
    if removals < 8:
        diffs.append(f"the driver observed only {removals} removals")
    verdict["removals"] = removals
    verdict["cases"] = len(CASES)

    if out_o != out_t:
        diffs.append(f"stdout differs ({out_o[:200]!r} vs {out_t[:200]!r})")

    verdict["diffs"] = diffs
    verdict["equivalent"] = not diffs
except Exception:
    verdict["error"] = traceback.format_exc(limit=8)

_emit(verdict)
VERDICT = verdict
