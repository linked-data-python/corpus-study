"""Validation driver for Haigutus__triplets__triplets_validation_shacl_ir.py___sparql_rows.

Establishes semantic equivalence of original.py and translated.ldpy.

`_sparql_rows(graph, SH, shape_uri, meta)` takes more than the single graph
argument the `fixture=` shortcut supports, so each fixture case parses
`fixture.ttl` fresh (once per side) and passes a plain `shape_uri` URIRef
plus a small stand-in `meta` dict.

`ordered=False`: `rows` is built by iterating `graph.objects(shape_uri,
SH.sparql)` / `m{ {shape_uri} {SH.sparql} ?sparql }`, and the original
never sorts -- no RDF store promises that order, so the row list is
compared as a multiset.

Calls added by the mutation audit of 2026-10-31 (each kills a mutant the
first two calls left alive -- `.one()` / `next(iter(...))` in place of
`.first()`, a widened subject, a truthiness guard):
  * _call_shape3 -- a NODE shape with no sh:path (as _node_expansion passes
    it, shacl_ir.py:96): `path` must be None, not a raise and not another
    shape's path; an EMPTY sh:select (row kept: `select is None` is false)
    and an EMPTY sh:message (row carries message ""); one declaration with
    two sh:prefix / two sh:namespace values (first one wins, no raise), one
    with no sh:namespace ("<None>" in the header).
  * _call_shape4 -- two sh:path IRIs, two sh:select and two sh:message
    values on one sh:sparql child: value() takes the first and never raises.
  * _call_bnode_shape -- a blank-node property shape, the usual form of the
    shapes _shape_rows hands to this region (shacl_ir.py:53).
"""
from pathlib import Path

from rdflib import Graph, Namespace

from rdfeval.harness import run_pair

FIXTURE = Path(__file__).parent / "fixture.ttl"
SH = Namespace("http://www.w3.org/ns/shacl#")
EX = Namespace("http://example.org/")


def _graph():
    return Graph().parse(str(FIXTURE), format="turtle")


def _call_shape1():
    # URIRef sh:path; a skipped no-select child, a full child (message +
    # two prefix declarations), and a bare child (no prefixes, no message).
    g = _graph()
    meta = {"shape_id": str(EX.Shape1), "marker": "meta-1"}
    return (g, SH, EX.Shape1, meta), {}


def _call_shape2():
    # Blank-node sh:path (path field must come back None) and zero
    # sh:sparql children at all (rows must come back []).
    g = _graph()
    meta = {"shape_id": str(EX.Shape2), "marker": "meta-2"}
    return (g, SH, EX.Shape2, meta), {}


def _call_shape3():
    g = _graph()
    meta = {"shape_id": str(EX.Shape3), "marker": "meta-3"}
    return (g, SH, EX.Shape3, meta), {}


def _call_shape4():
    g = _graph()
    meta = {"shape_id": str(EX.Shape4), "marker": "meta-4"}
    return (g, SH, EX.Shape4, meta), {}


def _call_bnode_shape():
    g = _graph()
    shape = g.value(EX.Holder, SH.property)
    meta = {"shape_id": "bnode", "marker": "meta-bn"}
    return (g, SH, shape, meta), {}


VERDICT = run_pair(
    __file__,
    entry='_sparql_rows',
    calls=[_call_shape1, _call_shape2, _call_shape3, _call_shape4,
           _call_bnode_shape],
    ordered=False,
)
