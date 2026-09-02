"""Validation driver for TeamWalabi__agriculture-image-metadata__agri_image_meta_utils_sparql_queries.py__query_find_platforms.

This region READS a graph, so the oracle is not isomorphism but the equality
of the values both versions produce from the same input graph (design record
corpus/405).  `fixture.ttl` is parsed fresh for each side.

Two calls: the fixture graph (several solutions, plus neighbouring triples
that must not match) and a fresh empty ``Graph()`` (the zero-solution case).
"""
from pathlib import Path

from rdflib import Graph

from rdfeval.harness import fixture_graph, run_pair

_FIXTURE = Path(__file__).resolve().parent / "fixture.ttl"

VERDICT = run_pair(
    __file__,
    entry='query_find_platforms',
    calls=[
        lambda: ((fixture_graph(_FIXTURE),), {}),
        lambda: ((Graph(),), {}),
    ],
    # ordered=True only if the region imposes an order (sorted, ORDER BY):
    # no store promises one, so results are compared as multisets.
)
