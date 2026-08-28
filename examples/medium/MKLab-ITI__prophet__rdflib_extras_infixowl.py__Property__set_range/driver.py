"""Validation driver: Property._set_range writes into self.graph.

The region is extracted as a free function still taking ``self``, so the
fixtures supply a small stand-in carrying the two attributes it touches
(``identifier`` and ``graph``).  The stand-in compares equal when the
identifiers match and the graphs are isomorphic, so the harness sees the
side effect of the call.  Fixtures cover the empty guard, the single-term
branch (plain Identifier and infixowl Class) and the iterable branch.
"""
from rdflib import Graph, Namespace, XSD

from infixowl_shim import Class
from rdfeval.harness import graphs_isomorphic, run_pair

EX = Namespace("http://example.com/")


class TermStub:
    def __init__(self, identifier, graph):
        self.identifier = identifier
        self.graph = graph

    def __eq__(self, other):
        return (isinstance(other, TermStub)
                and self.identifier == other.identifier
                and graphs_isomorphic(self.graph, other.graph))

    def __hash__(self):
        return hash(self.identifier)

    def __repr__(self):
        return "TermStub(%r, %d triples)" % (self.identifier, len(self.graph))


def no_range():
    return ((TermStub(EX.hasParent, Graph()), None), {})


def single_iri():
    return ((TermStub(EX.hasParent, Graph()), EX.Person), {})


def single_class():
    # classOrIdentifier unwraps an infixowl Class to its identifier; the
    # Class is built in its own scratch graph so the subject graph stays
    # untouched by the fixture itself.
    return ((TermStub(EX.hasParent, Graph()), Class(EX.Human, graph=Graph())),
            {})


def several_ranges():
    return ((TermStub(EX.hasAge, Graph()), [XSD.integer, EX.Age]), {})


VERDICT = run_pair(__file__, entry="_set_range",
                   calls=[no_range, single_iri, single_class, several_ranges])
