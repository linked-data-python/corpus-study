"""Validation driver for jupyter-naas__abi__libs_naas-abi-core_naas_abi_core_utils_validate_bfo_ontology.py__check_inverse_of_itself.

This region READS a graph (`g.value(prop, OWL.inverseOf)` per prop in
main_properties), so the oracle is not isomorphism of a graph the region
builds but the equality of what the two versions produce from the same input
(design record corpus/405): `fixture.ttl` is parsed fresh for each side and
fed as `g`; `main_properties` is the driver's second argument.

The fixture (see its header) covers several solutions of the pattern in the
graph, the zero-solution case (`.value()`/`.first()` -> None), and a
neighbourhood -- another self-inverse property -- that must not be reached
because it is deliberately left out of `main_properties`.
"""
from rdflib import URIRef

from rdfeval.harness import fixture_graph, run_pair

FIXTURE = "fixture.ttl"
MAIN_PROPERTIES = {
    URIRef("http://example.org/selfInverse"),
    URIRef("http://example.org/hasPart"),
    URIRef("http://example.org/partOf"),
    URIRef("http://example.org/noInverse"),
    # ex:otherSelfInverse deliberately excluded: it is self-inverse in the
    # fixture too, but must never be reached by this call.
}


def one_call():
    return ((fixture_graph(FIXTURE), set(MAIN_PROPERTIES)), {})


VERDICT = run_pair(
    __file__,
    entry='check_inverse_of_itself',
    fixture=FIXTURE,
    calls=[one_call],
    # ordered=True only if the region imposes an order (sorted, ORDER BY):
    # no store promises one, so results are compared as multisets. The loop
    # also walks a Python `set`, whose own iteration order is not a property
    # of the region either.
)
