"""Validation driver for Restriction.serialize (infixowl).

The region copies an owl:Restriction description into a target graph: it first
re-serialises the restricted property, then every triple of the restriction,
following owl:allValuesFrom / owl:someValuesFrom into the filler class.

The region is a method body, so the driver supplies a stand-in ``self`` with
the three attributes it reads (``onProperty``, ``graph``, ``identifier``).
The target graph is the second argument, so the harness compares it by
isomorphism after each call.
"""
from rdflib import BNode, Graph, OWL, RDF, RDFS, URIRef

from rdfeval.harness import graphs_isomorphic, run_pair

EX = "http://example.com/"
SOME_PROP = URIRef(EX + "someProp")
FOO = URIRef(EX + "Foo")


class _Restriction:
    """Stand-in for the infixowl Restriction being serialised."""

    def __init__(self, kind=OWL.someValuesFrom, filler=FOO):
        self.identifier = BNode("restriction")
        self.onProperty = SOME_PROP
        self.graph = Graph()
        # the restricted property, which the region re-serialises first
        self.graph.add((SOME_PROP, RDF.type, OWL.DatatypeProperty))
        self.graph.add((SOME_PROP, RDFS.label, URIRef(EX + "label")))
        # the restriction itself
        self.graph.add((self.identifier, RDF.type, OWL.Restriction))
        self.graph.add((self.identifier, OWL.onProperty, SOME_PROP))
        self.graph.add((self.identifier, kind, filler))
        # the filler class, reached only through allValuesFrom/someValuesFrom
        self.graph.add((filler, RDF.type, OWL.Class))
        self.graph.add((filler, RDFS.label, URIRef(EX + "FooLabel")))

    def __eq__(self, other):
        if not isinstance(other, _Restriction):
            return NotImplemented
        return (self.identifier == other.identifier
                and self.onProperty == other.onProperty
                and graphs_isomorphic(self.graph, other.graph))

    def __repr__(self):
        return "_Restriction(%s, %d triples)" % (self.identifier,
                                                 len(self.graph))


def some_values_from():
    return ((_Restriction(OWL.someValuesFrom), Graph()), {})


def all_values_from():
    return ((_Restriction(OWL.allValuesFrom), Graph()), {})


def max_cardinality():
    # a restriction kind the region must NOT follow into a filler class
    return ((_Restriction(OWL.maxCardinality, URIRef(EX + "Bar")), Graph()), {})


VERDICT = run_pair(__file__, entry="serialize",
                   calls=[some_values_from, all_values_from, max_cardinality])
