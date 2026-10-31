"""Validation driver for Haigutus__triplets__triplets_validation_shacl_ir.py___resolve_path.

Establishes semantic equivalence of original.py and translated.ldpy.

`_resolve_path(graph, SH, path_node)` takes more than the single graph
argument the `fixture=` shortcut supports, so each fixture case parses
`fixture.ttl` fresh (once per side, as `run_pair` requires for a graph
argument) and locates `path_node` in that fresh graph by a predicate/object
lookup that is unambiguous in the fixture -- `path_node` is usually a blank
node, and rdflib does not preserve blank-node labels across independent
parses, so it cannot be hard-coded as `BNode("...")`.  The values the
function *returns* are always `(str | None, bool, bool)`, never a raw graph
term, so this has no bearing on what gets compared.

Added by the mutation audit of 2026-10-31 (fixture.ttl, last section):
  * _call_two_inverse / _call_two_alternative -- TWO solutions for the
    inversePath and alternativePath reads; same local name either way, so
    the answer does not depend on order, while `.one()` raises.
  * _call_empty_inverse / _call_zero_nested -- falsy literal hits ("" and 0)
    where the region tests `is not None`, not truthiness.
  * _call_rest_only -- rdf:rest without rdf:first: the existence test must
    answer no although Graph.items() would follow the rest.
  * _call_literal -- path_node is a Literal, which graph.value(shape,
    SH.path) can return in the repository's callers (shacl_ir.py:87, 262,
    287) when a shape is malformed.
The alternative-path lookup of _call_alternative_nested_inverse now names
_:pAlt through its first item, since the fixture has several
sh:alternativePath subjects.
"""
from pathlib import Path

from rdflib import Graph, Literal, Namespace, RDF, URIRef

from rdfeval.harness import run_pair

FIXTURE = Path(__file__).parent / "fixture.ttl"
SH = Namespace("http://www.w3.org/ns/shacl#")
EX = Namespace("http://example.org/")
EX2 = Namespace("http://example.org/other#")


def _alt_owner(g, first_item):
    """The node whose sh:alternativePath list starts with `first_item`."""
    head = next(g.subjects(RDF.first, first_item))
    return next(g.subjects(SH.alternativePath, head))


def _graph():
    return Graph().parse(str(FIXTURE), format="turtle")


def _call_none():
    # path_node is None -- returns before touching the graph at all.
    return (Graph(), SH, None), {}


def _call_uriref():
    # isinstance(path_node, URIRef) -- also returns before any graph read.
    return (Graph(), SH, URIRef(EX.directProp)), {}


def _call_inverse():
    g = _graph()
    path_node = next(g.subjects(SH.inversePath, EX.prop2))
    return (g, SH, path_node), {}


def _call_alternative_nested_inverse():
    g = _graph()
    path_node = _alt_owner(g, next(g.subjects(SH.path, EX.noise)))
    return (g, SH, path_node), {}


def _call_sequence_via_type():
    g = _graph()
    path_node = next(g.subjects(RDF.first, EX.assocProp))
    return (g, SH, path_node), {}


def _call_sequence_too_long():
    g = _graph()
    path_node = next(g.subjects(RDF.first, EX.stepA))
    return (g, SH, path_node), {}


def _call_zero_solution():
    g = _graph()
    path_node = next(g.subjects(SH.path, EX.decoy))
    return (g, SH, path_node), {}


def _call_two_inverse():
    g = _graph()
    return (g, SH, next(g.subjects(SH.inversePath, EX.prop9))), {}


def _call_two_alternative():
    g = _graph()
    return (g, SH, _alt_owner(g, next(g.subjects(SH.inversePath, EX.prop8)))), {}


def _call_empty_inverse():
    g = _graph()
    return (g, SH, next(g.subjects(SH.inversePath, Literal("")))), {}


def _call_zero_nested():
    g = _graph()
    return (g, SH, _alt_owner(g, next(g.subjects(SH.inversePath, Literal(0))))), {}


def _call_rest_only():
    g = _graph()
    seq2 = next(g.subjects(RDF.first, EX.assocProp))
    return (g, SH, next(g.subjects(RDF.rest, seq2))), {}


def _call_literal():
    return (_graph(), SH, Literal("x")), {}


VERDICT = run_pair(
    __file__,
    entry='_resolve_path',
    calls=[
        _call_none,
        _call_uriref,
        _call_inverse,
        _call_alternative_nested_inverse,
        _call_sequence_via_type,
        _call_sequence_too_long,
        _call_zero_solution,
        _call_two_inverse,
        _call_two_alternative,
        _call_empty_inverse,
        _call_zero_nested,
        _call_rest_only,
        _call_literal,
    ],
)
