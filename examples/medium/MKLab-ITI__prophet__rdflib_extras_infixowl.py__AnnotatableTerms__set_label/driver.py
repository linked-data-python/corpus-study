"""Validation driver: AnnotatableTerms._set_label writes rdfs:label triples.

The region is a method body, so the driver supplies a stand-in ``self``
carrying the two attributes the region touches (``graph`` and
``identifier``).  Comparison is graph isomorphism on the mutated graph.
Both branches of the region are exercised: a single ``Identifier`` label
and an iterable of labels.
"""
from rdflib import Graph, Literal, URIRef

from rdfeval.harness import graphs_isomorphic, run_pair


class _Term:
    """Stand-in for an infixowl AnnotatableTerms instance."""

    def __init__(self):
        self.graph = Graph()
        self.identifier = URIRef("http://example.org/Pizza")

    def __eq__(self, other):
        if not isinstance(other, _Term):
            return NotImplemented
        return (self.identifier == other.identifier
                and graphs_isomorphic(self.graph, other.graph))


def single_identifier_label():
    return ((_Term(), Literal("Pizza", lang="en")), {})


def iterable_of_labels():
    return ((_Term(), [Literal("Pizza", lang="en"),
                       Literal("Pizze", lang="it")]), {})


def falsy_label():
    return ((_Term(), None), {})


VERDICT = run_pair(__file__, entry="_set_label",
                   calls=[single_identifier_label, iterable_of_labels,
                          falsy_label])
