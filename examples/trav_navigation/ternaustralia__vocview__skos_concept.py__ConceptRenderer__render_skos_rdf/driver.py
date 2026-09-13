"""Validation driver for ternaustralia__vocview__skos_concept.py__ConceptRenderer__render_skos_rdf.

This region READS a graph, so the oracle is not isomorphism but the equality
of the values both versions produce from the same input graph (design record
corpus/405).  `fixture.ttl` is parsed fresh for each side.

The fixture is part of the translation: it must hold several solutions of the
pattern the region reads, the zero-solution case, and neighbouring triples
that must NOT match.
"""
from rdfeval.harness import run_pair

# The region reads a module global (config.Config.g), not a parameter, and
# its entry point (`_render_skos_rdf`) takes a `self` rather than a graph --
# so this driver calls the `render(uri, fmt)` test wrapper instead of using
# fixture= (which would pass a freshly-parsed graph as the sole argument).
# fixture.ttl is still the input graph: config.py (the context shim) parses
# it once into Config.g -- see its header for why sharing that one parse
# between the two sides is safe here (the region only reads it).
VERDICT = run_pair(
    __file__,
    entry='render',
    calls=[
        lambda: (("http://example.org/concept1", "turtle"), {}),  # several
        # solutions plus a blank-node object whose own triples must be
        # pulled in too
        lambda: (("http://example.org/concept2", "turtle"), {}),  # the
        # neighbourhood, rendered on its own: concept1's triples must not
        # leak in either direction
        lambda: (("http://example.org/absent", "turtle"), {}),  # zero
        # solutions: not a subject of anything in the fixture
    ],
)
