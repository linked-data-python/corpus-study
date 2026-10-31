"""Validation driver for TeamWalabi__agriculture-image-metadata__agri_image_meta_utils_sparql_queries.py__query_find_platforms.

This region READS a graph, so the oracle is not isomorphism but the equality
of the values both versions produce from the same input graph (design record
corpus/405).  `fixture.ttl` is parsed fresh for each side.

Two calls: the fixture graph (several solutions, plus neighbouring triples
that must not match) and a fresh empty ``Graph()`` (the zero-solution case).
The harness compares the rows returned and the printed lines (stdout), in
store order on both sides.

Repair of 2026-10-31 (mutation audit).  `?platform ?p agimage:Platform`
(the rdf:type predicate widened) stayed green: nothing reached
agimage:Platform through another predicate.  fixture.ttl now holds
`ex:mention1 rdfs:seeAlso agimage:Platform` with a platformName (shares two
terms with the type pattern, must not appear) and `ex:platform4` with two
names, one the falsy "" (two rows, two printed lines).  The repository's
callers pass a plain `Graph` (tests/test_utils.py:284 on an empty one,
tests/test_ontology.py:151 and create_ontology.py:178 on a populated one)
and never use the return value; checked by hand that `s{ }(g)` binds no
prefix on `g` (create_ontology.py serialises `g` right after).
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
