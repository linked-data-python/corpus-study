"""Validation driver for ktbs__ktbs__lib_ktbs_api_base.py__BaseMixin_create_method.

Establishes semantic equivalence of original.py and translated.ldpy.
"""
from rdflib import Graph, RDF, URIRef

from context import KTBS
from rdfeval.harness import run_pair


class FakeBase:
    """Minimal stand-in for a ktbs TraceBase (BaseMixin's `self`).

    Only what create_method touches: `.uri`, `.state` (a graph already
    holding one Method, so the `trust` branch's membership test has
    something to check), `.post_graph` and `.factory` (both external I/O in
    the real class; here they just record the call and hand back the node).
    """

    def __init__(self):
        self.uri = URIRef("http://example.org/base1/")
        self.state = Graph()
        self.state.add((URIRef("http://example.org/base1/m1"), RDF.type,
                         KTBS.Method))
        self.posted = []

    def post_graph(self, graph, _id, _trust, node, _type):
        self.posted.append((graph, _id, _trust, node, _type))
        return [node]

    def factory(self, uri, _types):
        return uri

    # run_pair compares every argument passed to entry(), self included: two
    # fresh FakeBase instances (one per side) must compare equal on their
    # observable state, not by identity.
    def __eq__(self, other):
        return isinstance(other, FakeBase) and self.uri == other.uri \
            and set(self.state) == set(other.state)

    def __hash__(self):
        return hash(self.uri)


def _case_new_method():
    self = FakeBase()
    return (self,), {
        "parent": "m1",
        "parameters": {"foo": "1", "bar": "baz"},
        "label": "my method",
    }


def _case_explicit_id_no_label():
    self = FakeBase()
    return (self,), {
        "id": "m2",
        "parent": "http://example.org/other-base/m1/",
        "parameters": {},
    }


VERDICT = run_pair(
    __file__,
    entry="create_method",
    calls=[_case_new_method, _case_explicit_id_no_label],
)
