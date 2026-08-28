"""Validation driver: Individual._set_sameAs writes into self.graph.

The region is extracted as a free function still taking ``self``, so the
fixtures supply a small stand-in carrying the two attributes it touches
(``identifier`` and ``graph``).  The stand-in compares equal when the
identifiers match and the graphs are isomorphic, so the harness sees the
side effect of the call.  Fixtures cover the single-term branch (plain
Identifier and infixowl Class, the two shapes classOrIdentifier accepts)
and the iterable branch.
"""
from rdflib import Graph, Namespace

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


def single_iri():
    return ((TermStub(EX.alice, Graph()), EX.aliceBis), {})


def single_class():
    # classOrIdentifier unwraps an infixowl Class to its identifier; the
    # Class is built in its own scratch graph so the subject graph stays
    # untouched by the fixture itself.
    return ((TermStub(EX.alice, Graph()), Class(EX.aliceTer, graph=Graph())),
            {})


def several_terms():
    return ((TermStub(EX.alice, Graph()),
             [EX.a1, EX.a2, EX.a3]), {})


VERDICT = run_pair(__file__, entry="_set_sameAs",
                   calls=[single_iri, single_class, several_terms])
