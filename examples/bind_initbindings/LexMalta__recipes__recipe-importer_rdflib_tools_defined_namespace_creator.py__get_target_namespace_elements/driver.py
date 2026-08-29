"""Validation driver for LexMalta__recipes__recipe-importer_rdflib_tools_defined_namespace_creator.py__get_target_namespace_elements.

This region READS a graph (a SELECT with an OPTIONAL and a namespace-prefix
FILTER) and returns computed values, so the oracle is not isomorphism but
the equality of the values both versions produce from the same input graph
(design record corpus/405) -- meta.json's `oracle` was corrected from the
pipeline's default "isomorphism" to "values" for this reason: the automated
categoriser missed the `g.query(...)` call (categories: {}, rdf_ops: 0),
most likely because the query text is built through `.replace("xxx", ...)`
rather than a plain literal.

`fixture.ttl` is parsed fresh for each side, and each call also resets the
`lexmalta_context.args.target_namespace` global the region reads alongside
its own `target_namespace` parameter (see lexmalta_context.py) -- both
representations import the *same* shim module, so the assignment is visible
to whichever of original.py / translated.ldpy is executing.

Two calls: one with a target namespace that has member elements (three
distinct OPTIONAL branches -- dcterms:description, rdfs:comment,
skos:definition -- plus one member with none of the three, to exercise the
OPTIONAL's unbound/`str(None)` path), and one whose namespace has zero
members in the same graph (the zero-solution case).
"""
from pathlib import Path

from rdfeval.harness import fixture_graph, run_pair

FIXTURE = Path(__file__).resolve().parent / "fixture.ttl"


def call(target_namespace):
    def _make():
        from lexmalta_context import args
        args.target_namespace = target_namespace
        graph = fixture_graph(FIXTURE)
        return (graph, target_namespace), {}
    return _make


VERDICT = run_pair(
    __file__,
    entry="get_target_namespace_elements",
    fixture="fixture.ttl",
    calls=[
        call("http://example.org/ns#"),        # several solutions
        call("http://example.org/zzz#"),        # zero solutions
    ],
)
