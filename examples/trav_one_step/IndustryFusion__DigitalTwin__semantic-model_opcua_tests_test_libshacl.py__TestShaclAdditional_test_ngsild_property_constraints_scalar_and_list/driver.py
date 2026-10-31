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

Added by the 2026-10-31 mutation audit.  With the library as it is, every
read has exactly one solution and every assertion passes, so the first call
could not tell `next(...)` from `.first()`, nor see an assertion removed.
Two additions:

- the stand-in's assert methods keep a JOURNAL (method, members with blank
  nodes masked, outcome), compared by `__eq__`; their failure messages are
  masked the same way, since a BNode label differs between the two sides;
- four more calls run the region against a REGRESSED library -- a `Shacl`
  subclass that breaks one thing the test exists to catch, identical for
  both sides.  A test region's behaviour is how it fails as much as that it
  passes:
    no_list_property    the list shape lost its sh:property: `next()` raises
                        StopIteration, where `.first()` gives None and
                        `(None, sh:path, hasValueList) in g` is a wildcard
                        that passes in silence;
    no_scalar_property  the same for the scalar shape (the first read);
    wrong_list_path     the list property has sh:path hasValue: `found`
                        stays False and `assertTrue(found)` must fail;
    aux_property_first  the library emits a helper node's sh:property
                        before the shape's own (as get_array_validation_shape
                        does in the list case): a read whose subject was
                        widened would pick the helper's.
"""
from rdflib import BNode, Graph, Namespace
from rdflib.compare import to_isomorphic
from rdflib.namespace import SH

from rdfeval.harness import run_pair
from context_shim import Shacl


def _masked(value):
    """A term or tuple of terms with blank nodes masked: their labels differ
    between the two sides."""
    if isinstance(value, tuple):
        return tuple(_masked(v) for v in value)
    return "_:b" if isinstance(value, BNode) else value


class _NoListProperty(Shacl):
    def get_ngsild_property_constraints(self, value_rank, *args, **kwargs):
        shapes = super().get_ngsild_property_constraints(value_rank, *args, **kwargs)
        if value_rank is not None:
            for shape in shapes:
                self.shaclg.remove((shape, SH.property, None))
        return shapes


class _NoScalarProperty(Shacl):
    def get_ngsild_property_constraints(self, value_rank, *args, **kwargs):
        shapes = super().get_ngsild_property_constraints(value_rank, *args, **kwargs)
        if value_rank is None:
            for shape in shapes:
                self.shaclg.remove((shape, SH.property, None))
        return shapes


class _WrongListPath(Shacl):
    def get_ngsild_property_constraints(self, value_rank, *args, **kwargs):
        shapes = super().get_ngsild_property_constraints(value_rank, *args, **kwargs)
        for inner in list(self.shaclg.subjects(SH.path, self.ngsildns['hasValueList'])):
            self.shaclg.remove((inner, SH.path, self.ngsildns['hasValueList']))
            self.shaclg.add((inner, SH.path, self.ngsildns['hasValue']))
        return shapes


class _AuxPropertyFirst(Shacl):
    def get_ngsild_property_constraints(self, *args, **kwargs):
        helper, helper_inner = BNode("helper"), BNode("helper_inner")
        self.shaclg.add((helper, SH.property, helper_inner))
        self.shaclg.add((helper_inner, SH.path, self.ngsildns['hasJSON']))
        return super().get_ngsild_property_constraints(*args, **kwargs)


class _Fixture:
    """Stand-in for TestShaclAdditional.setUp(): only the attributes and
    assert methods this region reads or calls (self.sh, self.data_graph,
    self.assertTrue, self.assertIn)."""

    def __init__(self, shacl=Shacl):
        self.data_graph = Graph()
        self.sh = shacl(self.data_graph, "http://example.org/",
                        Namespace("http://example.org/base/"),
                        Namespace("http://example.org/opcua/"))
        self.journal = []

    def assertTrue(self, expr, msg=None):
        self.journal.append(("assertTrue", bool(expr)))
        if not expr:
            raise AssertionError(msg if msg is not None else f"{expr!r} is not true")

    def assertIn(self, member, container, msg=None):
        self.journal.append(("assertIn", _masked(member), member in container))
        if member not in container:
            raise AssertionError(
                msg if msg is not None else f"{_masked(member)!r} not found")

    def __eq__(self, other):
        if not isinstance(other, _Fixture):
            return NotImplemented
        return (self.journal == other.journal
                and to_isomorphic(self.sh.shaclg) == to_isomorphic(other.sh.shaclg)
                and to_isomorphic(self.data_graph) == to_isomorphic(other.data_graph))

    def __repr__(self):
        return f"_Fixture(journal={self.journal!r})"


VERDICT = run_pair(
    __file__,
    entry='test_ngsild_property_constraints_scalar_and_list',
    calls=[lambda: ((_Fixture(),), {}),
           # regressed libraries (audit 2026-10-31), see the docstring
           lambda: ((_Fixture(_NoListProperty),), {}),
           lambda: ((_Fixture(_NoScalarProperty),), {}),
           lambda: ((_Fixture(_WrongListPath),), {}),
           lambda: ((_Fixture(_AuxPropertyFirst),), {})],
)
