"""Validation driver for meaningfy-ws__cm2shacl__src_cm2shacl_utils.py__combine_shapes_with_same_path.

This region READS a graph, so the oracle is not isomorphism but the equality
of the values both versions produce from the same input graph (design record
corpus/405).  `fixture.ttl` is parsed fresh for each side.

The fixture is part of the translation: it must hold several solutions of the
pattern the region reads, the zero-solution case, and neighbouring triples
that must NOT match.
"""
from rdfeval.harness import run_pair

VERDICT = run_pair(
    __file__,
    entry='combine_shapes_with_same_path',
    fixture="fixture.ttl",
    # ordered=True only if the region imposes an order (sorted, ORDER BY):
    # no store promises one, so results are compared as multisets.
)
