"""Validation driver: canonicalName(term, g) is a pure read of the graph.

The region is a closure defined inside Property.__repr__; extracted, it is a
plain function.  Fixtures cover its four branches: blank node, XSD datatype,
boolean class expression (repr), and named term (qname).
"""
from rdflib import BNode, Graph, Namespace, RDF, URIRef, XSD
from rdflib.collection import Collection
from rdflib.namespace import NamespaceManager

from infixowl_context import Class

from rdfeval.harness import run_pair

OWL = Namespace("http://www.w3.org/2002/07/owl#")
EX = Namespace("http://example.org/")


def _graph():
    g = Graph()
    g.namespace_manager.bind("ex", EX, override=False)
    g.namespace_manager.bind("owl", OWL, override=False)
    return g


def bnode_term():
    g = _graph()
    return ((BNode("anon"), g), {})


def xsd_term():
    g = _graph()
    return ((XSD.integer, g), {})


def boolean_class_term():
    """C owl:unionOf ( ex:A ex:B ) — canonicalName falls back on repr()."""
    g = _graph()
    head = BNode("union")  # stable id: the fixture is built once per side
    Collection(g, head, [EX.A, EX.B])
    g.add((EX.C, RDF.type, OWL.Class))
    g.add((EX.C, OWL.unionOf, head))
    return ((Class(EX.C, graph=g), g), {})


def named_term():
    """A named class: canonicalName ends on str(term.qname).

    infixowl.Class is used rather than Property because Class defines
    __eq__/__hash__ (by identifier), so the harness can compare the argument
    the two runs received; Property inherits identity comparison.
    """
    g = _graph()
    g.add((EX.Knows, RDF.type, OWL.Class))
    return ((Class(EX.Knows, graph=g), g), {})


VERDICT = run_pair(__file__, entry="canonicalName",
                   calls=[bnode_term, xsd_term, boolean_class_term,
                          named_term])
