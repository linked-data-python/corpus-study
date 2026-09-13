"""Validation driver for jupyter-naas__abi__libs_naas-abi-core_naas_abi_core_services_object_storage_ontologies_modules_ObjectStorageEventOntology.py__RDFEntity_rdf.

Establishes semantic equivalence of original.py and translated.ldpy.

``rdf`` is written against duck-typed ``self`` objects (attribute access
only: ``_uri``, ``_class_uri``, ``label``, ``_property_uris``,
``_object_properties``). The fixtures below stand in for a real RDFEntity
subclass, and are rebuilt fresh for each call (and each side) since ``rdf``
mutates the ``visited`` set it is given.
"""
from rdflib import Graph, Literal, URIRef

from rdfeval.harness import run_pair


class Leaf:
    """A related entity with its own .rdf(), to exercise the recursive
    (object-valued) property branches without depending on the region
    under test for its own output."""

    def __init__(self, uri):
        self._uri = uri

    def rdf(self, subject_uri=None, visited=None):
        g = Graph()
        s = URIRef(subject_uri or self._uri)
        g.add((s, URIRef("http://example.org/leafMarker"), Literal(True)))
        return g

    def __eq__(self, other):
        return isinstance(other, Leaf) and self._uri == other._uri

    def __repr__(self):
        return f"Leaf({self._uri!r})"


class Entity:
    # __eq__/__repr__: the harness also compares call arguments (to catch a
    # region that mutates them differently), so these duck-typed fixtures
    # need value equality instead of the default identity comparison.
    def __eq__(self, other):
        return isinstance(other, Entity) and vars(self) == vars(other)

    def __repr__(self):
        return f"Entity({vars(self)!r})"


def make_entity():
    e = Entity()
    e._uri = "http://example.org/e1"
    e._class_uri = "http://example.org/C1"
    e.label = "Entity One"
    e._object_properties = {"child", "refs"}
    e._property_uris = {
        "value": "http://example.org/hasValue",
        "flag": "http://example.org/hasFlag",
        "child": "http://example.org/hasChild",
        "tags": "http://example.org/hasTag",
        "refs": "http://example.org/hasRef",
        "missing": "http://example.org/hasMissing",
    }
    e.value = 42
    e.flag = True
    e.child = Leaf("http://example.org/leaf1")
    e.tags = ["red", "blue"]
    e.refs = [URIRef("http://example.org/other1"), "http://example.org/other2"]
    # e.missing is deliberately absent: exercises getattr(..., None) -> skip
    return e


def case_full():
    return ((make_entity(),), {"subject_uri": None, "visited": None})


def case_bare():
    # No _class_uri, no label, no _property_uris at all.
    return ((Entity(),), {"subject_uri": "http://example.org/bare", "visited": None})


def case_cycle():
    uri = "http://example.org/e1"
    return ((make_entity(),), {"subject_uri": uri, "visited": {uri}})


VERDICT = run_pair(
    __file__,
    entry='rdf',
    calls=[case_full, case_bare, case_cycle],
)
