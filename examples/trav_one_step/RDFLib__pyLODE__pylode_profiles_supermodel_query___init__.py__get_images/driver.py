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

Four more calls (repair of 2026-10-30), one small subject each, so that
every single-value read decides something visible -- a shared subject
would let a "first found" read stop on the same node every time:

- ``ex:thing-bare``: an image with none of the six properties.  Each
  ``graph.value`` gives None; ``.first()`` must too (``.one()`` raises).
- ``ex:thing-double``: two values for each of the six properties, plus a
  description.  ``graph.value`` keeps the first stored triple and
  ``.first()`` must keep the same (``.one()`` raises); the description is
  the only input of ``get_descriptions``.
- ``ex:thing-falsy``: ``""``, ``""^^xsd:string`` and ``0``, returned as terms.
- ``ex:thing-unsorted``: five images stored against the sort key (the
  region's positional call puts the caption in ``.order``), so dropping
  ``sorted`` shows; two identical images, so dropping ``set`` shows.
"""
from pathlib import Path

from rdflib import URIRef

from rdfeval.harness import fixture_graph, run_pair

_FIXTURE = Path(__file__).resolve().parent / "fixture.ttl"

_WITH_IMAGES = URIRef("http://example.org/thing-with-images")
_WITHOUT_IMAGES = URIRef("http://example.org/thing-without-images")
_CASES = [URIRef("http://example.org/" + n) for n in
          ("thing-bare", "thing-double", "thing-falsy", "thing-unsorted")]

VERDICT = run_pair(
    __file__,
    entry='get_images',
    fixture="fixture.ttl",
    calls=[
        lambda: ((_WITH_IMAGES, fixture_graph(_FIXTURE)), {}),
        lambda: ((_WITHOUT_IMAGES, fixture_graph(_FIXTURE)), {}),
    ] + [
        (lambda iri=iri: ((iri, fixture_graph(_FIXTURE)), {}))
        for iri in _CASES
    ],
    ordered=True,
)
