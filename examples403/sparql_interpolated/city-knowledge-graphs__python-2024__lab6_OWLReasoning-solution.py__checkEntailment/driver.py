"""Validation driver for
city-knowledge-graphs__python-2024__lab6_OWLReasoning-solution.py__checkEntailment.

checkEntailment(g, triple) splices `triple` -- an arbitrary string, not a
term -- straight into the ASK query text via string concatenation. There is
no island form for this: s{ } only allows {expr} in *term* position, never
as query text. See meta.json ("not-expressible") for what exactly is out of
reach.

Fixtures exercise `triple` holding more than one term (a full pattern) and
even a variable, to show the interpolated text is not reducible to a single
term.
"""
from rdflib import Graph, Namespace, RDF

from rdfeval.harness import run_pair

EX = Namespace("http://example.org/")


def make_graph():
    g = Graph()
    g.bind("ex", EX)
    g.add((EX.a, RDF.type, EX.Sensor))
    g.add((EX.b, RDF.type, EX.Other))
    return g


VERDICT = run_pair(
    __file__,
    entry='checkEntailment',
    calls=[
        # a single triple, holds
        lambda: ((make_graph(),
                  "<http://example.org/a> a <http://example.org/Sensor>"), {}),
        # a single triple, does not hold
        lambda: ((make_graph(),
                  "<http://example.org/a> a <http://example.org/Other>"), {}),
        # `triple` is not even one term: a pattern with a variable
        lambda: ((make_graph(), "?s a <http://example.org/Sensor>"), {}),
    ],
)
