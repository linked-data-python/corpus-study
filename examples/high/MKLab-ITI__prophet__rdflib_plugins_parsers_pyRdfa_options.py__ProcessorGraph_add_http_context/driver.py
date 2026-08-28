"""Validation driver for MKLab-ITI__prophet__..._pyRdfa_options.py__ProcessorGraph_add_http_context.

The region is a method that mutates `self.graph`.  `self` is stood in for by a
minimal object whose only attribute is that graph and whose __eq__ compares it
by isomorphism, so the harness's argument comparison is the real check.
"""
from rdflib import BNode, Graph, URIRef

from rdfeval.harness import graphs_isomorphic, run_pair


class ProcessorGraph:
    """Stand-in for the ProcessorGraph instance the method is bound to."""

    def __init__(self):
        self.graph = Graph()

    def __eq__(self, other):
        return (isinstance(other, ProcessorGraph)
                and graphs_isomorphic(self.graph, other.graph))


def bnode_subject_404():
    return ((ProcessorGraph(), BNode(), 404), {})


def uriref_subject_200():
    return ((ProcessorGraph(), URIRef("http://example.org/error/1"), 200), {})


def labelled_bnode_503():
    return ((ProcessorGraph(), BNode("err"), "503"), {})


VERDICT = run_pair(__file__, entry="add_http_context",
                   calls=[bnode_subject_404, uriref_subject_200,
                          labelled_bnode_503])
