"""Validation driver for isamplesorg__vocabularies__tools_vocab2md.py__getNarrower.

This region READS a graph, so the oracle is not isomorphism but the equality
of the values both versions produce from the same input graph (design record
corpus/405).  `fixture.ttl` is parsed fresh for each side.

The fixture is part of the translation: it must hold several solutions of the
pattern the region reads, the zero-solution case, and neighbouring triples
that must NOT match.
"""
from pathlib import Path

from rdfeval.harness import run_pair, fixture_graph

FIXTURE = Path(__file__).resolve().parent / "fixture.ttl"


def call(v, r):
    return lambda: ((fixture_graph(FIXTURE), v, r), {})


VERDICT = run_pair(
    __file__,
    entry='getNarrower',
    calls=[
        call(None, "http://example.org/Animal"),                   # several solutions: Dog, Cat
        call("http://example.org/VocabA", "http://example.org/Animal"),  # scheme filter excludes Wolf
        call(None, "http://example.org/Rock"),                     # zero solutions
    ],
    # ordered=True only if the region imposes an order (sorted, ORDER BY):
    # no store promises one, so results are compared as multisets.
)
