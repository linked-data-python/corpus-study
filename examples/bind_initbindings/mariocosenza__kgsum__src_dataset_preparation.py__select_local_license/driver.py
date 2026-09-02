"""Validation driver for mariocosenza__kgsum__src_dataset_preparation.py__select_local_license.

This region READS a graph, so the oracle is not isomorphism but the equality
of the values both versions produce from the same input graph (design record
corpus/405).  `fixture.ttl` is parsed fresh for each side.

The fixture is part of the translation: it must hold several solutions of the
pattern the region reads, the zero-solution case, and neighbouring triples
that must NOT match.  `select_local_license(parsed_graph)` takes a single
graph argument and always finds *something or nothing* in it (no second
parameter to vary), so the zero-solution case needs a second graph with no
`dcterms:license` triple at all -- `calls=` supplies both explicitly instead
of relying on the single-call default `fixture=` alone would build.
"""
from pathlib import Path

from rdflib import Graph

from rdfeval.harness import fixture_graph, run_pair

FIXTURE = Path(__file__).resolve().parent / "fixture.ttl"


def _empty_graph():
    g = Graph()
    g.parse(data="""
        @prefix ex: <http://example.org/> .
        @prefix dcterms: <http://purl.org/dc/terms/> .
        ex:dataset4 dcterms:title "No license here" .
    """, format="turtle")
    return g


VERDICT = run_pair(
    __file__,
    entry='select_local_license',
    fixture="fixture.ttl",
    calls=[
        lambda: ((fixture_graph(FIXTURE),), {}),  # several solutions, plus neighbourhood
        lambda: ((_empty_graph(),), {}),           # zero-solution case
    ],
    # ordered=True only if the region imposes an order (sorted, ORDER BY):
    # no store promises one, so results are compared as multisets.
)
