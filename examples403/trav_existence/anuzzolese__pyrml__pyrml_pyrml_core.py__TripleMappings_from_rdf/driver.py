"""Validation driver for anuzzolese__pyrml__pyrml_pyrml_core.py__TripleMappings_from_rdf.

This region READS a graph, so the oracle is not isomorphism but the equality
of the values both versions produce from the same input graph (design record
corpus/405).  `fixture.ttl` is parsed fresh for each side.

`from_rdf(g, parent=None)` has two shapes worth exercising separately, so
`calls=` supplies them explicitly instead of relying on the single-graph
default:

  * call_no_parent -- parent=None: `tm` stays None (the SUBJECT WILDCARD
    case), so every triples-map subject in the whole graph reachable via
    rml:logicalSource OR rr:logicalTable is a candidate. Of the three
    candidates in the fixture, ex:tmB has NO rr:subjectMap -- the
    zero-solution / False branch of `bool(m{ {tm} rr:subjectMap ?x })` --
    while ex:tmA and ex:tmD do, so both branches of the region's one true
    existence check are exercised in a single call that still returns
    normally (no assert to dodge here, unlike the two LA3D regions of this
    batch: `from_rdf` just skips appending and returns).
  * call_with_parent -- parent=ex:refMap: `tm` resolves via
    `m{ {parent} rr:parentTriplesMap ?tm }.first()` to ex:tmC, which
    restricts `tps` to subject=ex:tmC only -- exercising the `.first()`
    read, and proving the untranslated `g.triples(...)` line's subject
    scoping still holds when the translated `.first()` feeds it: ex:tmA/B/D
    must NOT appear in this call's result even though they satisfy the
    predicate-path pattern too.

The two calls together give the region's only genuine existence idiom
(`bool(m{ {tm} rr:subjectMap ?x })`) both a true and a false solution in the
same run -- something the two LA3D regions of this batch could not do
because their reads are guarded by bare asserts instead of a graceful `if`.
"""
from pathlib import Path

from rdflib import URIRef

from rdfeval.harness import fixture_graph, run_pair

HERE = Path(__file__).resolve().parent
FIXTURE = HERE / "fixture.ttl"

REF_MAP = URIRef("http://example.org/refMap")


def call_no_parent():
    return ((fixture_graph(FIXTURE),), {})


def call_with_parent():
    return ((fixture_graph(FIXTURE), REF_MAP), {})


VERDICT = run_pair(
    __file__,
    entry='from_rdf',
    fixture="fixture.ttl",
    calls=[call_no_parent, call_with_parent],
    # ordered=True only if the region imposes an order (sorted, ORDER BY):
    # no store promises one, so results are compared as multisets.
)
