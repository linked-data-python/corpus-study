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
"""
from pathlib import Path

from rdfeval.harness import run_pair, fixture_graph

FIXTURE = Path(__file__).resolve().parent / "fixture.ttl"


def case(anchor):
    def make():
        return (fixture_graph(FIXTURE), anchor), {}
    return make


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
    ],
)
