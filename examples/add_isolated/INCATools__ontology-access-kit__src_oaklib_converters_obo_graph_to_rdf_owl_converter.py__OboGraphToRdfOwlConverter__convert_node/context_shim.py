# Context shim (see meta.json): minimal reconstruction of the objects that
# OboGraphToRdfOwlConverter._convert_node relies on -- the oaklib.datamodels
# .obograph node/meta dataclasses and the _uri_ref/_convert_meta helper
# methods it calls on self -- from INCATools/ontology-access-kit@5f88047efa9,
# so the region executes without the oaklib package installed.
# Identical bindings for both representations.
from dataclasses import dataclass, field
from typing import Optional

import rdflib

OBO = "http://purl.obolibrary.org/obo/"


class PropertyTypeEnum:
    OBJECT = "OBJECT"
    ANNOTATION = "ANNOTATION"
    DATA = "DATA"


@dataclass
class Meta:
    definition: Optional[str] = None
    xrefs: list = field(default_factory=list)
    synonyms: list = field(default_factory=list)


@dataclass
class Node:
    id: str = None
    lbl: Optional[str] = None
    type: Optional[str] = None
    propertyType: Optional[str] = None
    meta: Optional[Meta] = None


class Edge:
    pass


class Graph:
    pass


class GraphDocument:
    pass


class PropertyValue:
    pass


class Converter:
    """Stand-in for OboGraphToRdfOwlConverter, providing the helper
    methods ``_convert_node`` calls on ``self``.

    Stateless, so any two instances are interchangeable: ``__eq__`` says so
    to keep the harness's argument comparison (``self`` is call[i].arg[0])
    from failing on identity alone.
    """

    def __eq__(self, other):
        return isinstance(other, Converter)

    def __hash__(self):
        return hash(Converter)

    def _uri_ref(self, curie):
        if ":" not in curie:
            curie = f"obo:{curie}"
        prefix, local = curie.split(":", 1)
        if prefix == "obo":
            return rdflib.URIRef(OBO + local)
        return rdflib.URIRef(curie)

    def _convert_meta(self, uri, source, target):
        # Not exercised by the region under test (the fixtures below use
        # meta=None); kept so the guarded call on self resolves.
        return target
