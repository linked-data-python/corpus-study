"""Validation driver for LexMalta__recipes__recipe-importer_rdflib_extras_infixowl.py__BooleanClassExtentHelper___call____getExtent.

This region READS a graph, so the oracle is the equality of the values both
versions produce from the same input (design record corpus/405), not
isomorphism -- `fixture.ttl` is parsed fresh for each side. Unlike the usual
shape, the graph is not a function parameter: `_getExtent` reads the class
attribute `Individual.factoryGraph` (set by `BooleanClassExtentHelper.__call__`'s
caller in the real code -- `BooleanClass.getUnions`/`getIntersections`, see
context_shim.py), so each call below assigns it directly rather than passing
it positionally.

`_getExtent()` returns a generator of `BooleanClass` instances. The harness's
`materialise()` walks any iterable it does not special-case, and `BooleanClass`
is itself iterable (`OWLRDFListProxy.__iter__`, over its rdf:List members) --
so each side's result materialises into a plain nested list of RDF terms
(one member-list per selected subject), which is what actually gets
compared. That sidesteps `BooleanClass.__eq__`/`__hash__` entirely (no need
to give the stand-in instances identity-independent equality), and is why no
custom comparison is needed here despite `self`/`Individual.factoryGraph`
being ordinary Python objects, not rdflib terms.
"""
from rdflib import Graph

from rdfeval.harness import fixture_graph, run_pair
from context_shim import Individual


def _call(fixture_path):
    def make():
        Individual.factoryGraph = (
            fixture_graph(fixture_path) if fixture_path is not None else Graph()
        )
        return (), {}
    return make


VERDICT = run_pair(
    __file__,
    entry='_getExtent',
    fixture="fixture.ttl",
    calls=[
        _call("fixture.ttl"),  # two solutions (c1, c2), one non-matching neighbour (c3)
        _call(None),           # zero solutions: an empty graph
    ],
    # ordered=True only if the region imposes an order (sorted, ORDER BY):
    # no store promises one, so results are compared as multisets (the
    # default here, since fixture= is set).
)
