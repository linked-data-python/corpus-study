"""Validation driver: BooleanClass.serialize copies a boolean class
description into a target graph, rebuilding its owl:intersectionOf list.

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

FIRE = URIRef("http://example.com/Fire")
WATER = URIRef("http://example.com/Water")


class _BooleanClass:
    """Stand-in for the infixowl BooleanClass instance being serialised."""

    def __init__(self):
        self.identifier = BNode("boolean_class")
        self._operator = OWL.intersectionOf
        self._rdfList = [FIRE, WATER]
        self.graph = Graph()
        # the source description: the boolean class itself …
        self.graph.add((self.identifier, RDF.type, OWL.Class))
        self.graph.add((self.identifier, RDFS.label, URIRef("http://x/l")))
        # … a stale operator triple, which the region must not copy …
        self.graph.add((self.identifier, self._operator, BNode("old_list")))
        # … and the members CastClass will re-serialise.
        self.graph.add((FIRE, RDF.type, OWL.Class))
        self.graph.add((WATER, RDF.type, OWL.Class))

    def _serialize(self, graph):
        pass

    def __eq__(self, other):
        if not isinstance(other, _BooleanClass):
            return NotImplemented
        return (self.identifier == other.identifier
                and self._operator == other._operator
                and self._rdfList == other._rdfList
                and graphs_isomorphic(self.graph, other.graph))


def two_members():
    return ((_BooleanClass(), Graph()), {})


VERDICT = run_pair(__file__, entry="serialize", calls=[two_members])
