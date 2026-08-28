"""Validation driver for Class.__init__ (infixowl).

The region is a constructor body, extracted as a module-level function.  Its
``self`` must really be an infixowl ``Class`` -- ``super(Class, self)`` walks
the MRO and the five attribute assignments at the end go through the class's
property setters -- so the driver instantiates an uninitialised subclass of
``rdflib.extras.infixowl.Class`` (the same context shim both representations
import) and lets the region initialise it.

Every fixture passes an explicit fresh ``graph``: with ``graph=None`` infixowl
falls back to the CLASS-LEVEL ``Individual.factoryGraph``, which the two
executions would then share, and the region's ``(id, rdf:type, owl:Class) not
in self.graph`` test would see the other side's triples.
"""
from rdflib import Graph, Literal, RDF, RDFS, OWL, URIRef
from rdflib.extras.infixowl import Class

from rdfeval.harness import graphs_isomorphic, normalise, run_pair

EX = "http://example.org/ns#"
PIZZA = URIRef(EX + "Pizza")
FOOD = URIRef(EX + "Food")
DESSERT = URIRef(EX + "Dessert")


class Owner(Class):
    """An infixowl Class the region is about to initialise itself."""

    def __init__(self):  # deliberately does NOT call Class.__init__
        pass

    __hash__ = Class.__hash__

    def __eq__(self, other):
        return (isinstance(other, Owner)
                and normalise(self.identifier) == normalise(other.identifier)
                and self.qname == other.qname
                and graphs_isomorphic(self.graph, other.graph))

    def __repr__(self):
        return "Owner(%r, %d triples)" % (self.identifier, len(self.graph))


def plain():
    return ((Owner(), PIZZA), {"graph": Graph()})


def anonymous():
    # identifier=None -> infixowl mints a fresh BNode
    return ((Owner(),), {"graph": Graph()})


def skip_membership():
    return ((Owner(), PIZZA), {"graph": Graph(),
                               "skipOWLClassMembership": True})


def already_a_restriction():
    g = Graph()
    g.add((PIZZA, RDF.type, OWL.Restriction))
    return ((Owner(), PIZZA), {"graph": g})


def already_a_class():
    g = Graph()
    g.add((PIZZA, RDF.type, OWL.Class))
    g.add((PIZZA, RDFS.label, Literal("Pizza")))
    return ((Owner(), PIZZA), {"graph": g})


def with_axioms():
    return ((Owner(), PIZZA), {"graph": Graph(),
                               "subClassOf": [FOOD],
                               "equivalentClass": [URIRef(EX + "Pizze")],
                               "disjointWith": [DESSERT],
                               "complementOf": Class(DESSERT, graph=Graph(),
                                                     skipOWLClassMembership=True),
                               "comment": [Literal("a round flat bread")]})


VERDICT = run_pair(__file__, entry="__init__",
                   calls=[plain, anonymous, skip_membership,
                          already_a_restriction, already_a_class, with_axioms])
