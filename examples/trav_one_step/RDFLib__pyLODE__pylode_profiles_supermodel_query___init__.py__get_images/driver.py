"""Validation driver for RDFLib__pyLODE__pylode_profiles_supermodel_query___init__.py__get_images.

This region READS a graph, so the oracle is not isomorphism but the equality
of the values both versions produce from the same input graph (design record
corpus/405).  `fixture.ttl` is parsed fresh for each side.

``get_images(iri, graph)`` takes TWO arguments, so the default
``fixture=``-only wiring (a single positional graph argument) does not fit:
``calls=`` is supplied explicitly instead, pairing an ``iri`` with a fresh
parse of the fixture for each call.  Two calls exercise both the several-
solutions case (``ex:thing-with-images``, two images) and the zero-solution
case (``ex:thing-without-images``, no ``sdo:image`` at all); the fixture also
carries ``ex:neighbour``'s image, which must never appear in either result.

The region itself calls ``sorted(...)`` on its result, so order is part of
its meaning: ``ordered=True``.
"""
from pathlib import Path

from rdflib import URIRef

from rdfeval.harness import fixture_graph, run_pair

_FIXTURE = Path(__file__).resolve().parent / "fixture.ttl"

_WITH_IMAGES = URIRef("http://example.org/thing-with-images")
_WITHOUT_IMAGES = URIRef("http://example.org/thing-without-images")

VERDICT = run_pair(
    __file__,
    entry='get_images',
    fixture="fixture.ttl",
    calls=[
        lambda: ((_WITH_IMAGES, fixture_graph(_FIXTURE)), {}),
        lambda: ((_WITHOUT_IMAGES, fixture_graph(_FIXTURE)), {}),
    ],
    ordered=True,
)
