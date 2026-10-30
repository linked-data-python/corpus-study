"""Validation driver for jupyter-naas__abi__libs_naas-abi-core_naas_abi_core_services_object_storage_ontologies_modules_ObjectStorageEventOntology.py__RDFEntity_rdf.

Establishes semantic equivalence of original.py and translated.ldpy.

``rdf`` is written against duck-typed ``self`` objects (attribute access
only: ``_uri``, ``_class_uri``, ``label``, ``_property_uris``,
``_object_properties``). The fixtures below stand in for a real RDFEntity
subclass, and are rebuilt fresh for each call (and each side) since ``rdf``
mutates the ``visited`` set it is given.

Repair of 2026-10-30: the duck-typed fixtures are joined by pydantic replicas
of the two classes this module defines, ``ObjectPut`` and ``ObjectDeleted``
(same fields, same ``_property_uris``, same model_config), filled with the
values the repository really gives them -- ``ObjectStorageService.py:57,69,74``
passes ``prefix``/``key`` as str and ``size_bytes`` as an int (0 for an empty
payload), ``EventService.publish`` sets ``created_at`` to a tz-aware UTC
datetime, ``label`` stays None (so ``rdfs:label`` receives ``None``), and
``EventCodec``'s JSON reconstruction can give ``creator: Any`` a str, a
number, a bool, a dict or a list.  ``from_iri``'s permissive
``model_construct`` path can leave a field holding an ill-typed ``Literal``
(``toPython()`` returns the literal itself).  Every one of these goes through
the bare ``{x}`` interpolation that replaced ``Literal(x)``; the comparison
is graph isomorphism, so datatype and lexical form are compared term by
term.  ``case_visited_leaf`` puts a child's IRI in ``visited``: the
``if item._uri not in visited`` guard must then skip the child's own triples.
"""
import datetime
from typing import Any, ClassVar

from pydantic import BaseModel
from rdflib import Graph, Literal, URIRef, XSD

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


def case_visited_leaf():
    # The child leaf1 was already serialised by the caller: its marker
    # triple must not be added again, only the hasChild link.
    return ((make_entity(),), {"subject_uri": None,
                               "visited": {"http://example.org/leaf1"}})


_PROPS = {
    "created": "http://purl.org/dc/terms/created",
    "created_at": "http://ontology.naas.ai/abi/createdAt",
    "creator": "http://purl.org/dc/terms/creator",
    "key": "http://ontology.naas.ai/abi/object_storage/key",
    "label": "http://www.w3.org/2000/01/rdf-schema#label",
    "prefix": "http://ontology.naas.ai/abi/object_storage/prefix",
}


class ObjectDeleted(BaseModel):
    """Replica of the generated pydantic class (fields and class attributes
    as in ObjectStorageEventOntology.py; LogProcess adds nothing rdf reads)."""
    _uri: str = ""
    _class_uri: ClassVar[str] = "http://ontology.naas.ai/abi/object_storage/ObjectDeleted"
    _property_uris: ClassVar[dict] = dict(_PROPS)
    _object_properties: ClassVar[set[str]] = set()
    model_config = {"arbitrary_types_allowed": True, "extra": "forbid"}
    prefix: str | None = None
    key: str | None = None
    created_at: datetime.datetime | None = None
    label: str | None = None
    created: datetime.datetime | None = None
    creator: Any | None = None


class ObjectPut(ObjectDeleted):
    _class_uri: ClassVar[str] = "http://ontology.naas.ai/abi/object_storage/ObjectPut"
    _property_uris: ClassVar[dict] = dict(
        _PROPS, size_bytes="http://ontology.naas.ai/abi/object_storage/sizeBytes")
    size_bytes: int | None = None


def _with_uri(obj, uri):
    obj._uri = uri
    return obj


def case_object_put_service():
    # ObjectStorageService.put_object(prefix, key, b"") then publish():
    # str, str, int 0, tz-aware datetime, label None.
    evt = ObjectPut(prefix="datasets/2024", key="report.csv", size_bytes=0,
                    created_at=datetime.datetime(2026, 1, 2, 3, 4, 5,
                                                 tzinfo=datetime.UTC))
    return ((_with_uri(evt, "http://ontology.naas.ai/abi/evt-put-1"),), {})


def case_object_put_reconstructed():
    # A JSON-reconstructed event: naive datetime, empty label, creator given
    # every JSON shape (a list goes through the per-item branch).
    evt = ObjectPut(prefix="", key="a b/c.json", size_bytes=1234,
                    created_at=datetime.datetime(2026, 1, 2, 3, 4, 5, 600000),
                    label="", created=datetime.datetime(2025, 12, 31),
                    creator=["alice", 0, 1.5, True, "", {"id": 7}])
    return ((_with_uri(evt, "http://ontology.naas.ai/abi/evt-put-2"),), {})


def case_object_deleted_creator_scalar():
    evt = ObjectDeleted(prefix="p", key="k", creator=False,
                        created_at=datetime.datetime(2026, 1, 2,
                                                     tzinfo=datetime.UTC))
    return ((_with_uri(evt, "http://ontology.naas.ai/abi/evt-del-1"),), {})


def case_object_deleted_from_iri_fallback():
    # from_iri's model_construct fallback: an ill-typed xsd:dateTime literal
    # comes back from toPython() as the Literal itself; creator a number.
    evt = ObjectDeleted.model_construct(
        prefix="p", key="k", label="Deleted",
        created_at=Literal("not-a-date", datatype=XSD.dateTime), creator=3)
    return ((_with_uri(evt, "http://ontology.naas.ai/abi/evt-del-2"),), {})


VERDICT = run_pair(
    __file__,
    entry='rdf',
    calls=[case_full, case_bare, case_cycle, case_visited_leaf,
           case_object_put_service, case_object_put_reconstructed,
           case_object_deleted_creator_scalar,
           case_object_deleted_from_iri_fallback],
)
