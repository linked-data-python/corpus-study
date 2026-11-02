"""Validation driver for meaningfy-ws__cm2shacl__src_cm2shacl_utils.py__combine_shapes_with_same_path.

The region READS a SHACL graph, removes the dct:source of the property shapes,
detaches each node shape's property shapes, and attaches them back -- alone, or
merged into a new blank-node shape (sh:in lists concatenated, nodeKind /
datatype / class kept or turned into an sh:or list).  It returns the graph it
was given, so the oracle is that graph after the call, on both sides, from the
same input: the harness compares the return value and the argument (graph by
isomorphism, prefix bindings by name).

No shim: the region needs only rdflib and collections, both real.

The fixture covers: a node shape with three property shapes on one path (the
merge: two sh:in lists with an overlap, a nodeKind and a datatype that differ
between the shapes, so sh:or; classes), a path shared by two blank-node shapes
(an sh:or on nodeKind, one datatype), a property shape alone on its path (the
`len(shapes) == 1` branch, with its dct:source), a property shape WITHOUT
sh:path (g.value gives None: the original's `remove((ps, SH.path, None))`
is a wildcard that removes nothing, which an interpolated None would turn into
a TypeError), a property shape with TWO sh:path values (only the one that
g.value returns is removed), a node shape with no property shape, an orphan
property shape (its dct:source is collected by the second loop), and neighbours
that must not move: a dct:source on a non-shape, a list that is not an sh:in of
a grouped shape.

The sets in_values / nodeKinds / ... are iterated to build the RDF lists; their
order depends on the hash of the terms, identical on both sides because each
side is forked from this process.  Only IRIs and literals go in them.

Calls: the whole fixture; a graph with no node shape (zero solutions: the
first loops still strip dct:source); a graph with the shape without sh:path
alone.
"""
from pathlib import Path

from rdflib import Graph

from rdfeval.harness import fixture_graph, run_pair

HERE = Path(__file__).resolve().parent
FIXTURE = HERE / "fixture.ttl"

PREFIXES = """
@prefix ex:  <http://example.org/> .
@prefix dct: <http://purl.org/dc/terms/> .
@prefix sh:  <http://www.w3.org/ns/shacl#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
"""


def whole_fixture():
    return ((fixture_graph(FIXTURE),), {})


def no_node_shape():
    g = Graph()
    g.parse(data=PREFIXES + """
        ex:ps a sh:PropertyShape ; sh:path ex:p ; dct:source ex:s1 , ex:s2 .
        ex:other sh:property ex:ps2 .
        ex:ps2 dct:source ex:s3 ; sh:path ex:q .
    """, format="turtle")
    return ((g,), {})


def only_a_shape_without_path():
    g = Graph()
    g.parse(data=PREFIXES + """
        ex:N a sh:NodeShape ; sh:property ex:noPath , ex:withPath .
        ex:noPath sh:datatype xsd:string ; dct:source ex:src .
        ex:withPath sh:path ex:p .
    """, format="turtle")
    return ((g,), {})


VERDICT = run_pair(
    __file__,
    entry="combine_shapes_with_same_path",
    fixture="fixture.ttl",
    calls=[whole_fixture, no_node_shape, only_a_shape_without_path],
)
