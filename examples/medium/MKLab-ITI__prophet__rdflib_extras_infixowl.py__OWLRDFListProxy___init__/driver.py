"""Validation driver: OWLRDFListProxy.__init__ builds an RDF collection.

The region was extracted out of its class, so the driver supplies a minimal
stand-in for `self` (graph, identifier, _operator — the attributes the
constructor reads) and compares the resulting graph by isomorphism plus the
members of the collection that was built.
"""
from rdflib import BNode, Graph, Namespace, URIRef
from rdflib.collection import Collection
from rdflib.compare import to_isomorphic

from rdfeval.harness import run_pair

OWL = Namespace("http://www.w3.org/2002/07/owl#")
EX = Namespace("http://example.org/")


def _members(collection):
    if collection is None:
        return None
    return ["_:bnode" if isinstance(t, BNode) else t for t in collection]


class StubProxy:
    """Stand-in for a BooleanClass instance under construction."""

    def __init__(self, identifier, operator, graph=None):
        self.identifier = identifier
        self._operator = operator
        self.graph = graph
        self._rdfList = None

    def __eq__(self, other):
        return (self.identifier == other.identifier
                and self._operator == other._operator
                and _members(self._rdfList) == _members(other._rdfList)
                and to_isomorphic(self.graph) == to_isomorphic(other.graph))


def fresh_list():
    """rdfList is None: a new collection is created and linked to the class."""
    g = Graph()
    g.add((EX.C, URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
           OWL.Class))
    stub = StubProxy(EX.C, OWL.intersectionOf)
    return ((stub,), {"rdfList": None, "members": [EX.A, EX.B],
                      "graph": g})


def existing_list():
    """rdfList given: members are appended to the existing collection."""
    g = Graph()
    head = BNode("existing")  # stable id: the fixture is built once per side
    Collection(g, head, [EX.A])
    g.add((EX.C, OWL.unionOf, head))
    stub = StubProxy(EX.C, OWL.unionOf)
    return ((stub,), {"rdfList": [head], "members": [EX.A, EX.B],
                      "graph": g})


VERDICT = run_pair(__file__, entry="__init__",
                   calls=[fresh_list, existing_list])
