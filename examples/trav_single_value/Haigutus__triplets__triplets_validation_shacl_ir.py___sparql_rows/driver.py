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


VERDICT = run_pair(
    __file__,
    entry='_sparql_rows',
    calls=[_call_shape1, _call_shape2],
    ordered=False,
)
