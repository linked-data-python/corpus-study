"""Validation driver for tableau__altimeter__altimeter_core_graph_links.py__SimpleLink_to_rdf.

Establishes semantic equivalence of original.py and translated.ldpy.

``to_rdf`` mutates the ``graph`` argument it is given (no return value), so
each call must hand it a fresh ``Graph`` and the harness compares that
argument afterwards.
"""
from rdflib import BNode, Graph, Namespace

from rdfeval.harness import run_pair


class Link:
    def __init__(self, pred, obj):
        self.pred = pred
        self.obj = obj

    def __eq__(self, other):
        # the harness also compares call arguments (to catch a region that
        # mutates them differently); Link has no natural equality otherwise.
        return isinstance(other, Link) and vars(self) == vars(other)

    def __repr__(self):
        return f"Link({self.pred!r}, {self.obj!r})"


NS = Namespace("http://example.org/link#")


def case_small_int():
    # datatype stays None: plain integer coercion.
    return ((Link("hasCount", 3), BNode(), NS, Graph(), None), {})


def case_large_int():
    # obj.obj > 2147483647: datatype forced to xsd:nonNegativeInteger.
    return ((Link("hasBigCount", 5000000000), BNode(), NS, Graph(), None), {})


def case_string():
    # not an int at all: datatype stays None, plain string literal.
    return ((Link("hasName", "widget-1"), BNode(), NS, Graph(), None), {})


def case_negative_int():
    # int but not over the threshold, and negative: datatype stays None.
    return ((Link("hasDelta", -42), BNode(), NS, Graph(), None), {})


VERDICT = run_pair(
    __file__,
    entry='to_rdf',
    calls=[case_small_int, case_large_int, case_string, case_negative_int],
)
