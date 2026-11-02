"""Validation driver for hidden-graph__rdflib-starlight__tests_integration_test_oxigraph_backend.py__TestOxigraphRoundTrip_test_contains.

The region is a test: it asserts that (alice knows bob) is absent from `sg`,
adds it, asserts it is present.  What it SHOWS is therefore the mutation of
`sg` (the triple appears), or an AssertionError.  `sg` is a plain rdflib
Graph here (the real fixture is an Oxigraph-backed graph), `self` is None
(unused by the region).

CALL_1 -- empty graph: both asserts pass, the triple is added.
CALL_2 -- the graph already holds the triple: the first assert raises
          AssertionError (a raise is compared like a value).
CALL_3 -- neighbours only (alice knows carol, bob knows alice, alice likes
          bob, a literal object "bob"): absence is still true, so a
          membership test that is too broad (any p, any o, string "bob")
          would raise here; one triple is added, the neighbours stay.
"""
from rdflib import Graph, Literal, URIRef

from rdfeval.harness import run_pair

EX = "http://example.org/"


def _call_1():
    return (None, Graph()), {}


def _call_2():
    sg = Graph()
    sg.add((URIRef(EX + "alice"), URIRef(EX + "knows"), URIRef(EX + "bob")))
    return (None, sg), {}


def _call_3():
    sg = Graph()
    sg.add((URIRef(EX + "alice"), URIRef(EX + "knows"), URIRef(EX + "carol")))
    sg.add((URIRef(EX + "bob"), URIRef(EX + "knows"), URIRef(EX + "alice")))
    sg.add((URIRef(EX + "alice"), URIRef(EX + "likes"), URIRef(EX + "bob")))
    sg.add((URIRef(EX + "alice"), URIRef(EX + "knows"), Literal("bob")))
    return (None, sg), {}


VERDICT = run_pair(
    __file__,
    entry="test_contains",
    calls=[_call_1, _call_2, _call_3],
)
