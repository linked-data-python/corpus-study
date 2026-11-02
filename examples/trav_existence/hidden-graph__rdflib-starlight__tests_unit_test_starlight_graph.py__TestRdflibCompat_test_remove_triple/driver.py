"""Validation driver for hidden-graph__rdflib-starlight__tests_unit_test_starlight_graph.py__TestRdflibCompat_test_remove_triple.

The region is a test method that only asserts, taking the pytest fixture `sg`
(a `StarlightGraph`, i.e. an rdflib Graph).  The `starlight` package is not
installed, so `sg` is a plain `rdflib.Graph`; `demo(sg)` (identical on both
sides) calls the test and returns "ok" with the final size, or the failed
assertion as a value.  The harness also compares the final content of `sg`,
so the neighbours below show that EXACTLY the one triple is removed.

Calls:
  1. empty graph                              -> ok, graph stays empty
  2. neighbours of the triple: same s+p with another object, same p+o with
     another subject, same s+o with another predicate, same s+p with a
     Literal "o" object, one unrelated triple  -> ok, all five survive
  3. the triple already present before the call (add is idempotent)
                                               -> ok, only the neighbour stays
  4. a Graph whose `remove` does nothing       -> assertion-failed (the `not in`
     assertion sees the triple still there); this is the failing side of
     the existence test
  5. a Graph whose `add` does nothing and which holds only a neighbour
                                               -> ok, neighbour survives

Not a call: a Graph subclass overriding `__contains__` but not `triples()`
(or the reverse) would make `... in sg` and `bool(m{ ... })` disagree, since
the island reads through `graph.triples()`.  StarlightGraph overrides both,
with the same coercion (see meta.json), so the pair does not exercise it.
"""
from rdflib import Graph, Literal, URIRef

from rdfeval.harness import run_pair

EX = "http://example.org/"
S, P, O = URIRef(EX + "s"), URIRef(EX + "p"), URIRef(EX + "o")


def _neighbours(g):
    g.add((S, P, URIRef(EX + "o2")))
    g.add((URIRef(EX + "s2"), P, O))
    g.add((S, URIRef(EX + "p2"), O))
    g.add((S, P, Literal("o")))
    g.add((URIRef(EX + "x"), URIRef(EX + "y"), URIRef(EX + "z")))
    return g


class NoRemoveGraph(Graph):
    def remove(self, triple):
        return self


class NoAddGraph(Graph):
    def add(self, triple):
        return self


def _present():
    g = Graph()
    g.add((S, P, O))
    g.add((S, P, URIRef(EX + "o2")))
    return g


def _no_add_with_neighbour():
    g = NoAddGraph()
    Graph.add(g, (S, P, URIRef(EX + "o2")))
    return g


VERDICT = run_pair(
    __file__,
    entry='demo',
    calls=[
        lambda: ((Graph(),), {}),
        lambda: ((_neighbours(Graph()),), {}),
        lambda: ((_present(),), {}),
        lambda: ((NoRemoveGraph(),), {}),
        lambda: ((_no_add_with_neighbour(),), {}),
    ],
)
