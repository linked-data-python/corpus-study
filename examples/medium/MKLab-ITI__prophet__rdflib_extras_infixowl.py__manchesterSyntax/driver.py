"""Validation driver: manchesterSyntax serialises an OWL expression to text.

It is a module-level function, so the driver calls it directly.  The fixtures
walk the branches: the three boolean constructors, the owl:Restriction forms
(allValuesFrom / someValuesFrom / cardinality), owl:complementOf, and the
final fall-through (SPARQL probe + compute_qname) for a named class.
"""
from rdflib import BNode, Graph, Literal, Namespace, RDF, RDFS, URIRef
from rdflib.collection import Collection

from rdfeval.harness import run_pair

OWL = Namespace("http://www.w3.org/2002/07/owl#")
EX = Namespace("http://example.org/")


def _graph():
    g = Graph()
    g.namespace_manager.bind("ex", EX, override=False)
    g.namespace_manager.bind("owl", OWL, override=False)
    return g


def _collection(g, label, members):
    head = BNode(label)  # stable id: the fixture is built once per side
    Collection(g, head, members)
    return head


def intersection_of_named():
    g = _graph()
    head = _collection(g, "inter", [EX.Fire, EX.Water])
    return ((head, g), {"boolean": OWL.intersectionOf})


def intersection_named_and_anonymous():
    """One named class and one restriction: the ' THAT ' form."""
    g = _graph()
    restr = BNode("restr")
    g.add((restr, RDF.type, OWL.Restriction))
    g.add((restr, OWL.onProperty, EX.hasPart))
    g.add((restr, OWL.someValuesFrom, EX.Water))
    head = _collection(g, "inter2", [EX.Fire, restr])
    return ((head, g), {"boolean": OWL.intersectionOf})


def union_of():
    g = _graph()
    head = _collection(g, "union", [EX.Fire, EX.Water])
    return ((head, g), {"boolean": OWL.unionOf})


def one_of():
    g = _graph()
    head = _collection(g, "enum", [Literal("a"), Literal("b")])
    return ((head, g), {"boolean": OWL.oneOf})


def restriction_all_values_from():
    g = _graph()
    restr = BNode("only")
    g.add((restr, RDF.type, OWL.Restriction))
    g.add((restr, OWL.onProperty, EX.hasPart))
    g.add((restr, OWL.allValuesFrom, EX.Water))
    return ((restr, g), {})


def restriction_labelled_property():
    """A property with an rdfs:label takes the quoted-label branch."""
    g = _graph()
    restr = BNode("some")
    g.add((restr, RDF.type, OWL.Restriction))
    g.add((restr, OWL.onProperty, EX.hasPart))
    g.add((EX.hasPart, RDFS.label, Literal("has part")))
    g.add((restr, OWL.someValuesFrom, EX.Water))
    return ((restr, g), {})


def restriction_cardinality():
    g = _graph()
    restr = BNode("card")
    g.add((restr, RDF.type, OWL.Restriction))
    g.add((restr, OWL.onProperty, EX.hasPart))
    g.add((restr, OWL.maxCardinality, Literal(2)))
    return ((restr, g), {})


def complement_of():
    g = _graph()
    node = BNode("compl")
    g.add((node, OWL.complementOf, EX.Fire))
    return ((node, g), {})


def named_class():
    """Fall-through: the SPARQL probe finds nothing, qname is returned."""
    g = _graph()
    g.add((EX.Fire, RDF.type, OWL.Class))
    return ((EX.Fire, g), {})


def named_class_with_label():
    g = _graph()
    g.add((EX.Fire, RDF.type, OWL.Class))
    g.add((EX.Fire, RDFS.label, Literal("Fire")))
    return ((EX.Fire, g), {})


VERDICT = run_pair(__file__, entry="manchesterSyntax",
                   calls=[intersection_of_named,
                          intersection_named_and_anonymous,
                          union_of, one_of,
                          restriction_all_values_from,
                          restriction_labelled_property,
                          restriction_cardinality,
                          complement_of, named_class,
                          named_class_with_label])
