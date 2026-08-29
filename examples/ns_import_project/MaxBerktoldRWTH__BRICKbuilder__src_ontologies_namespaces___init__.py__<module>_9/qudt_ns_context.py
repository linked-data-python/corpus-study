# Context shim (see meta.json): subset of
# src/ontologies/namespaces/qudt.py from
# MaxBerktoldRWTH/BRICKbuilder@28f0710933dc, so the region executes outside
# its package (`src.ontologies.namespaces.qudt` is a real dotted project
# path that does not resolve for a single extracted file). Identical
# bindings for both representations.
#
# QUDT/QUDTU/QUDTQK: real `DefinedNamespace` subclasses, transcribed with a
# reduced member set (a few real terms each, enough for the demo below to
# dereference) -- not the full vocabularies (qudt.py has many more members
# per class), which this region's own body (a single import line) never
# enumerates or otherwise depends on.
from rdflib.namespace import DefinedNamespace, Namespace
from rdflib import URIRef


class QUDT(DefinedNamespace):
    _NS = Namespace("http://qudt.org/schema/qudt/")
    hasQuantityKind: URIRef
    hasUnit: URIRef


class QUDTU(DefinedNamespace):
    _NS = Namespace("http://qudt.org/vocab/unit/")
    K: URIRef
    M: URIRef
    KG: URIRef


class QUDTQK(DefinedNamespace):
    _NS = Namespace("http://qudt.org/vocab/quantitykind/")
    Temperature: URIRef
    Length: URIRef


__namespaces__ = {"qudt": QUDT, "qudtu": QUDTU, "qudtqk": QUDTQK}
