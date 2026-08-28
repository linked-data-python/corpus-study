"""Validation driver for ProcessorGraph.add_triples.

The region is a method, so each fixture passes a stand-in `self` holding a
fresh processor Graph; the stand-in compares by graph isomorphism, so the
harness sees the triples both representations added.

datetime.datetime.utcnow() is frozen for the whole run (both sides import the
same `datetime` module object), otherwise the dcterms:date literal would
differ between the two executions for reasons unrelated to the translation.
"""
import datetime

from rdflib import Graph, URIRef
from rdflib.compare import isomorphic

from pyrdfa_shim import RDFA_Error, RDFA_Warning, RDFA_Info, ns_distill
from rdfeval.harness import run_pair


class _FrozenDateTime(datetime.datetime):
    @classmethod
    def utcnow(cls):
        return cls(2024, 5, 17, 12, 30, 0)


datetime.datetime = _FrozenDateTime


class ProcessorGraph:
    """Stand-in for the enclosing class: it owns the processor graph."""

    def __init__(self):
        self.graph = Graph()

    def __eq__(self, other):
        return isinstance(other, ProcessorGraph) and isomorphic(self.graph,
                                                                other.graph)

    def __hash__(self):
        return 0


class _Element:
    """Minimal DOM-ish node: add_triples reads .nodeName."""
    nodeName = "span"


def call(*args):
    return lambda: ((ProcessorGraph(),) + args, {})


VERDICT = run_pair(
    __file__,
    entry='add_triples',
    calls=[
        # no info class, no context, no node
        call("something went wrong", RDFA_Error, None, None, None),
        # info class + string context + DOM node (nodeName branch)
        call("bad @about", RDFA_Warning, ns_distill["UnresolvablePrefix"],
             "http://example.org/doc.html", _Element()),
        # URIRef context + node without nodeName (except branch)
        call("info", RDFA_Info, None, URIRef("http://example.org/doc2.html"),
             "div"),
        # falsy context: the http Request block is skipped
        call("no context", RDFA_Error, ns_distill["IncorrectPrefixDefinition"],
             "", None),
    ],
)
