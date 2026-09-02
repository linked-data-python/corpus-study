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
"""
from pathlib import Path

from rdflib import Graph, Namespace, RDF, URIRef

from rdfeval.harness import run_pair

FIXTURE = Path(__file__).parent / "fixture.ttl"
SH = Namespace("http://www.w3.org/ns/shacl#")
EX = Namespace("http://example.org/")


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
    path_node = next(g.subjects(SH.alternativePath, None))
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
    ],
)
