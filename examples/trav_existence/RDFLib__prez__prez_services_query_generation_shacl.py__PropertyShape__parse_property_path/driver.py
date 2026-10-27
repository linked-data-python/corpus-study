"""Validation driver for RDFLib__prez__prez_services_query_generation_shacl.py__PropertyShape__parse_property_path.

This region READS a graph, so the oracle is not isomorphism but the equality
of the values both versions produce from the same input graph (design record
corpus/405). `fixture.ttl` anchors seven SHACL path shapes at stable IRIs
(`ex:caseN ex:path ...`), since the blank nodes inside them are not stable
across two separate parses of the file.

The construction this stratum exists to exercise is
`if self.graph.value(pp, RDF.first):` -- translated as
`if bool(m{ {pp} rdf:first ?x }):`. case1 and case7 give it a TRUE reading
(sequence paths, built from Turtle's `( ... )` list syntax); case3 and case4
give it a FALSE / zero-solution reading (a single predicate-object blank
node that is never a list head -- also the neighbourhood for case1/case7's
list heads, since it carries predicates of its own but never rdf:first).
case2 never reaches the graph-reading branch at all (pp is a URIRef); case5
exercises sh:alternativePath and Collection(); case6 exercises sh:union,
whose members are routed through `_add_path_to_shape` rather than the return
value.

`entry` is the `demo` harness both files carry identically (see meta.json):
the region is a method returning a PropertyPath tree (or None) built from
plain dataclasses standing in for the real, pydantic-based hierarchy
(pydantic is not installed here -- see context_shim.py). `demo` looks up the
path node for a given case and runs the region against a fresh
`PropertyShapeStub`, returning `(result, union_calls)` so both observable
effects are compared.

Repair pass (2026-10-27).  Three things were added.

* The guard.  `value(pp, RDF.first)` is tested for TRUTH, not for existence:
  a list whose head is `""` or `0` is not taken for a list (the node then
  falls through to `predicate_objects` and raises "multiple predicate-objects").
  err7 and err8 pin that down; the first translation (`bool(m{ })`) entered
  the list branch and raised "Malformed RDF list structure" instead.
* The branches the first seven cases did not reach: sh:oneOrMorePath,
  sh:zeroOrOnePath, shext:bNodeDepth (case8-10), nesting through three
  levels and the empty sh:alternativePath / sh:union lists (case11-13).
* The RAISES.  Five of the region's `raise ValueError` are reachable from a
  graph (no predicate-object, several, unsupported construct, literal node,
  malformed list x2).  run_pair compares what a call raises (type and
  message), but these messages embed the blank-node id of the path node,
  which differs between the two parses of the fixture; so `raises()` below
  executes both artefacts itself, through the harness' own loader, and
  compares the exception TYPE and MESSAGE with the blank-node ids
  normalised.  A difference is reported as a failed verdict.  The "Unhandled path class" raise is dead
  code in the source (every key of PRED_TO_PATH_CLASS is either handled
  before or in the list of four), so no graph reaches it.
"""
import re
import sys
from pathlib import Path

from rdfeval import harness
from rdfeval.harness import run_pair, fixture_graph

FIXTURE = Path(__file__).resolve().parent / "fixture.ttl"


def case(anchor):
    def make():
        return (fixture_graph(FIXTURE), anchor), {}
    return make


ERRORS = ["err1", "err2", "err3", "err4", "err5", "err6", "err7", "err8", "err9"]


def _outcome(demo, anchor):
    """What `demo` does on one side: ('raised', type, message) or ('ok',)."""
    try:
        demo(fixture_graph(FIXTURE), anchor)
    except Exception as e:                        # noqa: BLE001 - compared
        msg = re.sub(r"\bn[0-9a-f]{32}b\d+\b", "<bnode>", str(e))
        return ("raised", type(e).__name__, msg)
    return ("returned",)


def raises():
    """Differences between the exceptions the two sides raise, per error case."""
    left, right = harness.sides_from_env()
    here = Path(__file__).resolve().parent
    ns_l, _ = harness._exec_artefact(here / left, "__original__")
    ns_r, _ = harness._exec_artefact(here / right, "__translated__")
    diffs = []
    for anchor in ERRORS:
        a, b = _outcome(ns_l["demo"], anchor), _outcome(ns_r["demo"], anchor)
        if a[0] != "raised":
            diffs.append(f"{anchor}: the original does not raise ({a}); "
                         "the case no longer exercises a raise")
        if a != b:
            diffs.append(f"{anchor}: raise differs ({a!r} vs {b!r})")
    return diffs


_RAISE_DIFFS = raises()
if _RAISE_DIFFS:
    harness._emit({"example": FIXTURE.parent.name, "equivalent": False,
                   "method": "raises", "diffs": _RAISE_DIFFS, "error": None})
    sys.exit(1)

VERDICT = run_pair(
    __file__,
    entry="demo",
    fixture="fixture.ttl",
    calls=[
        case("case1"),  # sequence path: TRUE existence branch
        case("case2"),  # plain URIRef: graph-reading branch not reached
        case("case3"),  # sh:inversePath: FALSE / zero-solution branch
        case("case4"),  # sh:zeroOrMorePath: another FALSE instance
        case("case5"),  # sh:alternativePath over an RDF list
        case("case6"),  # sh:union: return value is None
        case("case7"),  # sequence with a non-leaf (blank node) member
        case("case8"),  # sh:oneOrMorePath
        case("case9"),  # sh:zeroOrOnePath
        case("case10"),  # shext:bNodeDepth with a literal operand
        case("case11"),  # inverse of a sequence holding an alternative
        case("case12"),  # empty sh:alternativePath list
        case("case13"),  # empty sh:union list: returns None, no call
    ],
)
