"""Validation driver for LexMalta__recipes__recipe-importer_rdflib_plugins_sparql_results_rdfresults.py__RDFResult___init__.

This region READS a graph, so the oracle is not isomorphism but the equality
of the values both versions produce from the same input graph (design record
corpus/405).  `fixture.ttl` is parsed fresh for each side.

`__init__` has no useful return value (it is `__init__`): everything it
computes lands on `self`, so `self` is what run_pair compares as a mutated
call argument. `self` needs no methods -- only plain attribute
assignment -- so a stand-in `_Receiver` is enough; no context shim needed
for the `RS`/`Result` names, which are either declared inline in the region
(`RS = Namespace(...)`) or genuinely installed (`rdflib.query.Result`).

`self.vars`/`self.bindings` are built by iterating `rs:resultVariable` /
`rs:solution` / `rs:binding`, whose order is not part of the region's
meaning (no store promises one, and the region does not sort) -- exactly
what run_pair's own `_unordered()` normalises for a *returned* list or dict,
but `self` is an opaque object it cannot see inside. `_Receiver.__eq__`
below reimplements the same unordered/multiset principle one level deeper,
so run_pair's generic arg-comparison (which falls back to plain `a == b`
once its `_unordered()` bottoms out on a type it does not recognise) lands
on an honestly unordered comparison instead of an accidental
iteration-order dependency between the two implementations' own `m{ }` vs
`graph.objects()` traversal order.

Three calls: SELECT (fixture.ttl -- one result set with three solutions of
varying binding count, including one with NO bindings at all, plus
neighbouring triples that must NOT be picked up), ASK (a small inline
graph), and CONSTRUCT (an empty graph -- no rs:ResultSet at all, the
zero-solution case for the very first read in the region).
"""
from collections import Counter
from pathlib import Path

from rdflib import Graph
from rdflib.compare import to_isomorphic

from rdfeval.harness import run_pair, fixture_graph

FIXTURE = Path(__file__).resolve().parent / "fixture.ttl"

ASK_TTL = """
@prefix ex: <http://example.org/> .
@prefix rs: <http://www.w3.org/2001/sw/DataAccess/tests/result-set#> .
ex:rset a rs:ResultSet ;
    rs:boolean true .
"""


class _Receiver:
    """`self` stand-in for `RDFResult.__init__` -- see module docstring."""

    def __eq__(self, other):
        if not isinstance(other, _Receiver):
            return NotImplemented
        if getattr(self, "type", None) != getattr(other, "type", None):
            return False
        vars_self = set(getattr(self, "vars", None) or [])
        vars_other = set(getattr(other, "vars", None) or [])
        if vars_self != vars_other:
            return False
        bindings_self = getattr(self, "bindings", None)
        bindings_other = getattr(other, "bindings", None)
        if bindings_self is None or bindings_other is None:
            if bindings_self != bindings_other:
                return False
        else:
            def key(bindings):
                return Counter(frozenset(d.items()) for d in bindings)
            if key(bindings_self) != key(bindings_other):
                return False
        if getattr(self, "askAnswer", None) != getattr(other, "askAnswer", None):
            return False
        g_self = getattr(self, "graph", None)
        g_other = getattr(other, "graph", None)
        if isinstance(g_self, Graph) and isinstance(g_other, Graph):
            if to_isomorphic(g_self) != to_isomorphic(g_other):
                return False
        elif g_self != g_other:
            return False
        return True


def _case(graph_factory):
    return lambda: ((_Receiver(), graph_factory()), {})


VERDICT = run_pair(
    __file__,
    entry="__init__",
    fixture="fixture.ttl",
    calls=[
        _case(lambda: fixture_graph(FIXTURE)),
        _case(lambda: Graph().parse(data=ASK_TTL, format="turtle")),
        _case(Graph),
    ],
)
