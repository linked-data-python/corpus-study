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

Calls added by the repair of 2026-10-30 (triage: weak-oracle), each aimed
at a mutant that stayed green with the three calls above:

* ASK whose answer is `false` -- `askAnswer is not None` must classify it
  as ASK; the mutant `if askAnswer:` (a false literal treated as absent)
  turns it into a SELECT.
* ASK whose `rs:boolean` is a literal of an unknown datatype --
  `askAnswer.value` is None, so both sides must raise the same "Malformed
  boolean" exception. (A malformed `xsd:boolean` such as "maybe" does not
  reach the raise: rdflib 7.2.1 maps it to False, so it is not used.)
* the SELECT result given as a TEXT STREAM rather than a Graph, with
  `format="turtle"`: the region's `graph.parse(source, **kwargs)` branch.
  This is the input type rdflib itself passes (`Result.parse` ->
  `RDFResultParser.parse(source, **kwargs)` -> `RDFResult(source, ...)`,
  rdflib/query.py:198 and rdfresults.py in the LexMalta clone).
* a DAWG-style result graph built from blank nodes only (the shape of the
  real result-set files), with a binding that has rs:variable but NO
  rs:value (the zero-solution case of the innermost value read: the
  dict must hold None for that variable).
* a binding that has rs:value but NO rs:variable: `Variable(None)` raises
  TypeError on both sides; the mutant `Variable(m{...}.first() or "x")`
  does not raise.

fixture.ttl also gained neighbours sharing two of the three terms of a
pattern (`ex:NotAResultSet rs:solution ...`, `ex:mentionsType
ex:about rs:ResultSet`), so that widening the bound subject of
`{rs} rs:solution ?s` or the predicate of `?rs a rs:ResultSet` into a
variable changes the result.
"""
from io import StringIO
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

ASK_FALSE_TTL = """
@prefix ex: <http://example.org/> .
@prefix rs: <http://www.w3.org/2001/sw/DataAccess/tests/result-set#> .
ex:rset a rs:ResultSet ;
    rs:boolean false .
"""

ASK_MALFORMED_TTL = """
@prefix ex: <http://example.org/> .
@prefix rs: <http://www.w3.org/2001/sw/DataAccess/tests/result-set#> .
ex:rset a rs:ResultSet ;
    rs:boolean "maybe"^^ex:unknownDatatype .
"""

BNODE_SELECT_TTL = """
@prefix rs: <http://www.w3.org/2001/sw/DataAccess/tests/result-set#> .
@prefix ex: <http://example.org/> .
[] a rs:ResultSet ;
    rs:resultVariable "a", "b" ;
    rs:solution [ rs:binding [ rs:variable "a" ; rs:value ex:one ] ,
                             [ rs:variable "b" ; rs:value "two"@en ] ] ,
                [ rs:binding [ rs:variable "a" ; rs:value 3 ] ,
                             [ rs:variable "b" ] ] .
"""

NO_VARIABLE_TTL = """
@prefix rs: <http://www.w3.org/2001/sw/DataAccess/tests/result-set#> .
[] a rs:ResultSet ;
    rs:resultVariable "a" ;
    rs:solution [ rs:binding [ rs:value "orphan" ] ] .
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
        _case(lambda: Graph().parse(data=ASK_FALSE_TTL, format="turtle")),
        _case(lambda: Graph().parse(data=ASK_MALFORMED_TTL, format="turtle")),
        lambda: ((_Receiver(), StringIO(FIXTURE.read_text())),
                 {"format": "turtle"}),
        _case(lambda: Graph().parse(data=BNODE_SELECT_TTL, format="turtle")),
        _case(lambda: Graph().parse(data=NO_VARIABLE_TTL, format="turtle")),
    ],
)
