"""Validation driver for asmirnov69__pyjviz-poc__janitor_pyjviz.py__dump_dot_code.

This region READS a graph and returns dot source as a string (design record
corpus/405): the oracle is equality of the produced string, not graph
isomorphism, so `fixture.ttl` is parsed fresh for each side and passed as
`dump_dot_code`'s sole argument.

Two calls: the populated fixture (two clusters, a labelled one and a
"none"-labelled one, each exercising all five queries, plus a stray
neighbourhood tagged with a CMC that is itself untyped and so must not
appear at all; and inter-cmc edges, method-call, method-call-arg and
method-return, running from a dataframe of one cmc to a method of the other,
so that the `?df <pyj:cmc> {cmc}` and the `?m <pyj:cmc> {cmc}` constraints of
the two edge queries are each needed on their own) and an empty graph (the zero-CMC case, `cmcs == []`).
"""
from rdflib import Graph

from rdfeval.harness import fixture_graph, run_pair


def _call(fixture_path):
    def make():
        g = fixture_graph(fixture_path) if fixture_path is not None else Graph()
        return (g,), {}
    return make


VERDICT = run_pair(
    __file__,
    entry='dump_dot_code',
    fixture="fixture.ttl",
    calls=[
        _call("fixture.ttl"),  # two clusters + a non-matching stray neighbourhood
        _call(None),           # zero solutions: an empty graph, no cmcs at all
    ],
    # The dot text embeds node numbering that depends on solution order, so
    # the region's own output is order-sensitive; both sides query an
    # equivalent rdflib store the same way, so `ordered=True`.
    ordered=True,
)
