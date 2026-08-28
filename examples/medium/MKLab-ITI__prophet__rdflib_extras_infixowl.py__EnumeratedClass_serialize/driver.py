"""Validation driver: EnumeratedClass.serialize copies an owl:oneOf class
description into a target graph, rebuilding its member list.

The region is a method body, so the driver supplies a stand-in ``self``
holding exactly the attributes it reads (``_rdfList``, ``graph``,
``identifier``, ``_operator``) and a no-op ``_serialize`` — the real
``Class._serialize`` (lines 917-925) walks subClassOf / equivalentClass /
disjointWith / complementOf, all empty for this fixture.
The target graph is passed as the second argument, so the harness compares
it by isomorphism after each call.
"""
from rdflib import BNode, Graph, OWL, RDF, RDFS, URIRef

from rdfeval.harness import graphs_isomorphic, run_pair

CHIME = URIRef("http://example.com/chime")
UCHE = URIRef("http://example.com/uche")
EJIKE = URIRef("http://example.com/ejike")


class _EnumeratedClass:
    """Stand-in for the infixowl EnumeratedClass instance being serialised."""

    def __init__(self, members):
        self.identifier = URIRef("http://example.com/ogbujicBros")
        self._operator = OWL.oneOf
        self._rdfList = list(members)
        self.graph = Graph()
        # the source description: the enumerated class itself …
        self.graph.add((self.identifier, RDF.type, OWL.Class))
        self.graph.add((self.identifier, RDFS.label, URIRef("http://x/l")))
        # … a stale owl:oneOf triple, which the region must not copy …
        self.graph.add((self.identifier, self._operator, BNode("old_list")))
        # … and the members CastClass will re-serialise.
        for _m in self._rdfList:
            self.graph.add((_m, RDF.type, OWL.Thing))

    def _serialize(self, graph):
        pass

    def __eq__(self, other):
        if not isinstance(other, _EnumeratedClass):
            return NotImplemented
        return (self.identifier == other.identifier
                and self._operator == other._operator
                and self._rdfList == other._rdfList
                and graphs_isomorphic(self.graph, other.graph))


def three_members():
    return ((_EnumeratedClass([CHIME, UCHE, EJIKE]), Graph()), {})


def no_member():
    return ((_EnumeratedClass([]), Graph()), {})


VERDICT = run_pair(__file__, entry="serialize",
                   calls=[three_members, no_member])
