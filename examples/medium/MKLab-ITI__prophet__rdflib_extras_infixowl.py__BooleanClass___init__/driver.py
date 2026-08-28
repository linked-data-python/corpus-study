"""Validation driver: BooleanClass.__init__ builds an owl:intersectionOf /
owl:unionOf list in ``graph``.

The region is an unbound ``__init__``; the fixtures supply an uninitialised
BooleanClass instance as ``self`` (``Class.__init__`` uses ``super(Class,
self)``, so ``self`` has to be a real Class subclass) plus the arguments.
Equality of that stand-in is identifier + operator + graph isomorphism; the
``graph`` keyword argument is compared by isomorphism by the harness itself.
"""
from rdflib import Graph, OWL, URIRef
from rdflib.collection import Collection

from infixowl_context import BooleanClass
from rdfeval.harness import graphs_isomorphic, run_pair

EX = "http://example.org/"


class BooleanSelf(BooleanClass):
    """An allocated-but-uninitialised BooleanClass: the region *is* its __init__."""

    def __init__(self):  # noqa: D107 - deliberately does not call super()
        pass

    def __eq__(self, other):
        return (isinstance(other, BooleanSelf)
                and self.identifier == other.identifier
                and self._operator == other._operator
                and graphs_isomorphic(self.graph, other.graph))

    __hash__ = BooleanClass.__hash__


def default_intersection():
    """Default operator (the owl:intersectionOf default argument), fresh graph."""
    return ((BooleanSelf(),),
            {"identifier": URIRef(EX + "MeatyPizza"),
             "members": [URIRef(EX + "Pizza"), URIRef(EX + "MeatyThing")],
             "graph": Graph()})


def explicit_union():
    return ((BooleanSelf(),),
            {"identifier": URIRef(EX + "PizzaOrPasta"),
             "operator": OWL.unionOf,
             "members": [URIRef(EX + "Pizza"), URIRef(EX + "Pasta")],
             "graph": Graph()})


def operator_from_graph():
    """operator=None: the operator is discovered with triples_choices()."""
    g = Graph()
    identifier = URIRef(EX + "MeatyPizza")
    cell = Collection(g, URIRef(EX + "list0"),
                      [URIRef(EX + "Pizza"), URIRef(EX + "MeatyThing")])
    g.add((identifier, OWL.intersectionOf, cell.uri))
    return ((BooleanSelf(),),
            {"identifier": identifier, "operator": None,
             "members": None, "graph": g})


VERDICT = run_pair(__file__, entry="__init__",
                   calls=[default_intersection, explicit_union,
                          operator_from_graph])
