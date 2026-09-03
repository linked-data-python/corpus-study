"""Validation driver for IndustryFusion__DigitalTwin__semantic-model_shacl2flink_lib_shacl_properties_to_sql.py__attribute_shapes.

This region READS a graph -- it is a generator over `g.subjects()`/
`g.objects()` matches, not a graph builder -- so the oracle is the equality
of the VALUES both versions produce from the same input graph (design record
corpus/405), not isomorphism. See meta.json: the pipeline's `"oracle":
"isomorphism"` is corrected to `"values"` here for exactly this reason (its
static heuristic missed the graph reads because the `g` parameter carries no
type annotation in the source, so `categories` above shows no `graph_read`
at all).

`attribute_shapes` returns a generator; `run_pair`'s `materialise()` drains
it on both sides before comparing, as an unordered multiset (no store
promises an iteration order, and neither version sorts).

One call against fixture.ttl (five attribute shapes reached through a plain
sh:property, an sh:and collection, a nested sh:or two connectives deep, and
an sh:not branch -- plus neighbours that must NOT match: an NGSI-LD value
path, an rdf:type path, a property shape with two sh:path values, and a
whole node shape with no sh:targetClass), and one call against an empty
graph for the zero-solution case.
"""
from pathlib import Path

from rdflib import Graph

from rdfeval.harness import run_pair, fixture_graph

FIXTURE = Path(__file__).resolve().parent / "fixture.ttl"


def _case(graph_factory):
    return lambda: ((graph_factory(),), {})


VERDICT = run_pair(
    __file__,
    entry="attribute_shapes",
    fixture="fixture.ttl",
    calls=[
        _case(lambda: fixture_graph(FIXTURE)),
        _case(Graph),
    ],
)
