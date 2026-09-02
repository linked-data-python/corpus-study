"""Validation driver for IndustryFusion__DigitalTwin__semantic-model_opcua_tests_test_libshacl.py__TestShaclAdditional_test_create_datatype_and_iri_shapes_and_shacl_or.

This region READS a graph, so the oracle is not isomorphism but the equality
of the values both versions produce from the same input graph (design record
corpus/405).  `fixture.ttl` is parsed fresh for each side.

The fixture is part of the translation: it must hold several solutions of the
pattern the region reads, the zero-solution case, and neighbouring triples
that must NOT match.
"""
import unittest

from rdfeval.harness import run_pair
from rdflib import Graph, Namespace
from rdflib.compare import to_isomorphic
from context_shim import Shacl


class _Fixture(unittest.TestCase):
    """Stand-in for the unittest.TestCase instance (``self``) the region
    runs as a bound method of.  It carries the same ``self.sh`` the real
    ``TestShaclAdditional.setUp`` builds; nothing else in the region uses
    ``self``.

    ``__eq__`` compares the *post-call* state of ``self.sh.shaclg`` by RDF
    isomorphism -- the harness compares every call argument, and this is
    the one that actually matters: the region's whole observable effect,
    beyond the assertions it runs internally, is the mutation it leaves in
    that graph (the datatype-shape add, the injected/removed triple, the
    sh:or collection).
    """

    def __init__(self):
        super().__init__()
        self.sh = Shacl(Graph(), "http://example.org/",
                         Namespace("http://example.org/base/"),
                         Namespace("http://example.org/opcua/"))

    def __eq__(self, other):
        return to_isomorphic(self.sh.shaclg) == to_isomorphic(other.sh.shaclg)

    def __hash__(self):
        return 0


# This region is a self-contained unittest test: it builds the shapes it
# reads back in the same function body (create_datatype_shapes,
# create_iri_shape, shacl_or all write to self.sh.shaclg before the
# assertions read it), so there is no external input graph to hand it --
# no fixture.ttl is used.  The oracle is twofold: the assertions raise if
# either side disagrees with the expected values, and the harness's
# argument comparison (via _Fixture.__eq__ above) checks the two sides
# left the same graph behind.
VERDICT = run_pair(
    __file__,
    entry='test_create_datatype_and_iri_shapes_and_shacl_or',
    calls=[lambda: ((_Fixture(),), {})],
)
