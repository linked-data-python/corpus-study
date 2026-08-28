"""Validation driver for Property.__init__.

The region is infixowl's ``Property.__init__`` lifted out of its class, so
it still calls ``super(Property, self).__init__`` and needs a real
``Property`` instance as ``self``.  ``Probe`` is a ``Property`` subclass
with an inert constructor (the region's ``__init__`` is what we call) and
an equality that is graph isomorphism, so the harness can compare the
mutated ``self``.
"""
from rdflib import Graph, URIRef

from rdfeval.harness import run_pair, graphs_isomorphic

from infixowl_context import OWL_NS, Property

EX = "http://example.org/"


class Probe(Property):
    """A Property whose own constructor does nothing."""

    def __init__(self):  # noqa: D107 - deliberately inert
        pass

    def __eq__(self, other):
        return (self.identifier == other.identifier
                and self._baseType == other._baseType
                and graphs_isomorphic(self.graph, other.graph))

    def __repr__(self):
        return f"Probe({self.identifier!r}, baseType={self._baseType!r})"


def case_default_base_type():
    return ((Probe(),), {"identifier": URIRef(EX + "p"), "graph": Graph()})


def case_explicit_base_type():
    return ((Probe(),), {"identifier": URIRef(EX + "p"), "graph": Graph(),
                         "baseType": OWL_NS.DatatypeProperty})


def case_type_already_asserted():
    g = Graph()
    g.add((URIRef(EX + "p"), URIRef(
        "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
        OWL_NS.ObjectProperty))
    return ((Probe(),), {"identifier": URIRef(EX + "p"), "graph": g})


def case_introspected_base_type():
    g = Graph()
    g.add((URIRef(EX + "p"), URIRef(
        "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
        OWL_NS.AnnotationProperty))
    return ((Probe(),), {"identifier": URIRef(EX + "p"), "graph": g,
                         "baseType": None})


VERDICT = run_pair(__file__, entry="__init__",
                   calls=[case_default_base_type, case_explicit_base_type,
                          case_type_already_asserted,
                          case_introspected_base_type])
