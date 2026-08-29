"""Validation driver for IndustryFusion__DigitalTwin__semantic-model_opcua_tests_test_libshacl.py__TestShaclAdditional_test_ngsild_property_constraints_scalar_and_list.

The region is a unittest method that takes `self` and reads back a SHACL
graph that `self.sh.get_ngsild_property_constraints(...)` -- a method of the
`Shacl` class (context_shim.py), not part of the region itself -- has just
built.  There is no externally-supplied graph to parse from a Turtle
fixture (the common case in design record corpus/405's "values" oracle):
what this region reads is a graph its own call chain produces, so
`fixture.ttl` does not apply here and is intentionally absent.

`calls=` supplies one call, built from a stand-in for the real
`TestShaclAdditional.setUp()` (see context_shim.py for the class it
constructs), freshly instantiated for EACH side -- required because the
region itself mutates `self.sh.shaclg` (`self.sh.shaclg = Graph()`, twice,
then populated by the calls under test), so the two sides cannot share one
instance the way a read-only argument could (contrast the swrl2rdf driver in
trav_single_value, which shares one read-only PrefixMap instead of adding it
an __eq__). The stand-in below defines its own `__eq__`, comparing
`.sh.shaclg` and `.data_graph` by RDF isomorphism -- without it, the
harness's generic object comparison would report the two freshly-built (but
behaviourally identical) instances as differing on every run, a false
negative unrelated to the translation.
"""
from rdflib import Graph, Namespace
from rdflib.compare import to_isomorphic

from rdfeval.harness import run_pair
from context_shim import Shacl


class _Fixture:
    """Stand-in for TestShaclAdditional.setUp(): only the attributes and
    assert methods this region reads or calls (self.sh, self.data_graph,
    self.assertTrue, self.assertIn)."""

    def __init__(self):
        self.data_graph = Graph()
        self.sh = Shacl(self.data_graph, "http://example.org/",
                         Namespace("http://example.org/base/"),
                         Namespace("http://example.org/opcua/"))

    def assertTrue(self, expr, msg=None):
        if not expr:
            raise AssertionError(msg if msg is not None else f"{expr!r} is not true")

    def assertIn(self, member, container, msg=None):
        if member not in container:
            raise AssertionError(
                msg if msg is not None else f"{member!r} not found in {container!r}")

    def __eq__(self, other):
        if not isinstance(other, _Fixture):
            return NotImplemented
        return (to_isomorphic(self.sh.shaclg) == to_isomorphic(other.sh.shaclg)
                and to_isomorphic(self.data_graph) == to_isomorphic(other.data_graph))


VERDICT = run_pair(
    __file__,
    entry='test_ngsild_property_constraints_scalar_and_list',
    calls=[lambda: ((_Fixture(),), {})],
)
