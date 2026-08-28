"""Validation driver: AnnotatableTerms._set_comment writes into self.graph.

The region is extracted as a free function still taking ``self``, so the
fixtures supply a small stand-in carrying the two attributes it touches
(``identifier`` and ``graph``).  The stand-in compares equal when the
identifiers match and the graphs are isomorphic, so the harness sees the
side effect of the call.  The three fixtures cover the three paths: the
empty guard, the single-Identifier branch and the iterable branch.
"""
from rdflib import Graph, Literal, Namespace

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


def no_comment():
    return ((TermStub(EX.Thing, Graph()), None), {})


def single_literal():
    return ((TermStub(EX.Thing, Graph()), Literal("a plain comment")), {})


def several_comments():
    return ((TermStub(EX.Thing, Graph()),
             [Literal("une note", lang="fr"),
              Literal("a note", lang="en"),
              EX.seeThisInstead]), {})


VERDICT = run_pair(__file__, entry="_set_comment",
                   calls=[no_comment, single_literal, several_comments])
