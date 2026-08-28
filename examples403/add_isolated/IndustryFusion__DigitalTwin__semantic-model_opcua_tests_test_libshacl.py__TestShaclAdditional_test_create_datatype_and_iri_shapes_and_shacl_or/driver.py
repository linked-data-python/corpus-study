"""Validation driver for IndustryFusion__DigitalTwin__semantic-model_opcua_tests_test_libshacl.py__TestShaclAdditional_test_create_datatype_and_iri_shapes_and_shacl_or.

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
    entry='test_create_datatype_and_iri_shapes_and_shacl_or',
    fixture="fixture.ttl",
    # ordered=True only if the region imposes an order (sorted, ORDER BY):
    # no store promises one, so results are compared as multisets.
)
