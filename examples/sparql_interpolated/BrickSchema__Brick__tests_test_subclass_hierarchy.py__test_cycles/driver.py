"""Validation driver for BrickSchema__Brick__tests_test_subclass_hierarchy.py__test_cycles.

`test_cycles()` reads a module-global `g` in the extracted region -- no
parameter, no visible RDF op until you notice the global (rdf_ops: 0 in
meta.json). The signature gained a `g=g` default so a call can hand it a
fresh graph per side: the "annotated parameter" remedy AGENT_BATCH.md
prescribes for this shape of region. The function BODY is byte-for-byte the
extracted original; only the parameter list changed, and identically on both
sides.

What the pair must agree on is the test's outcome: it returns None on a
hierarchy without a cycle and raises AssertionError, whose message lists the
looping edges, on one with a cycle.  `run_pair` compares the two raises by
exception type and message, so the interpolated loop body (`{BRICK[
minify(brick_class)]}`, the term the stratum is about) is exercised by the
cyclic cases below -- the earlier claim that it could not be, because the
harness stops at the first raise, was true of an older harness only.

The original rebuilds each class as the PREFIXED NAME `brick:%s` %
minify(brick_class), where `minify` keeps what follows the last '#'.  So it
looks at the cycle through `brick:<local name>`, whatever namespace
`brick_class` really lives in.  The translation reproduces exactly that
(`BRICK[minify(brick_class)]`), not the full IRI of `brick_class`: the
earlier translation interpolated the full IRI, which agrees on cycles inside
the Brick namespace but raises on a cycle in another namespace where the
original does not (case 4 below, which that translation failed).

Fixtures are Turtle text parsed fresh for each side (`_graph`); the assertion message prints a set, so
the cyclic cases use `_OrderedGraph`, whose rows come in a fixed order.

CALLS
  0  fixture.ttl, a deep acyclic Brick excerpt with a redundant edge: None.
  1  a two-cycle A <-> B in the Brick namespace with a class D hanging off
     it that is not on the cycle (D must not be reported): AssertionError.
  2  a three-cycle with a chord (A -> B -> C -> A and A -> C), plus a
     self-loop S -> S (with a class below it) and an unrelated class:
     AssertionError.
  3  two disjoint cycles plus an acyclic branch: AssertionError.
  4  a cycle in another namespace that has a '#' (rec#P <-> rec#Q) beside
     Brick classes: the original only looks at brick:P and brick:Q, which
     are not on a cycle, so it returns None -- and so must the translation.
  5  the same, with brick:P and brick:Q existing as plain parent/child (a
     local-name collision): still None.
  6  a Brick cycle AND a cycle in another namespace: the message lists only
     the Brick edges.
  7  an acyclic hierarchy with an owl:Restriction blank node as a parent
     (as in Brick.ttl): None.
  8  an empty graph: None.
  9  rec#P <-> rec#Q with brick:P below rec#Q (brick:P has only outgoing
     edges, so it is on no cycle): None.  Separates the two interpolations:
     a translation that uses the full IRI for the second one only is
     rejected here.
  10 the same with rec#Q below brick:P (rec#Q -> brick:P): None;
     rejects the full IRI for the first interpolation only.
  11 three Brick cycles in a chain (X<->Y, Y -> C, C<->D, D -> Z, Z<->W):
     only the edges inside a cycle are reported, none of the Y -> C or
     D -> Z bridges: AssertionError.
  12 a four-cycle A -> B -> C -> D -> A: the property path `+` in both
     interpolated patterns is needed (a single step would miss edges):
     AssertionError.
  13 a lone self-loop S -> S with a class below it: one looping edge, so
     the assertion must fire on a single element: AssertionError.

Mutants of translated.ldpy run on a copy and rejected by this driver: the
earlier translation (full IRI `{brick_class}` for both occurrences, calls 4,
5, 6, 9, 10), the full IRI for the first only (call 10) or the second only
(call 9), `BRICK[brick_class]` without `minify`, `?s rdfs:subClassOf+ ?s`
for the first (calls 10, 11), `?o rdfs:subClassOf+ ?o` for the second
(calls 9, 11), a single step instead of `+` in both (calls 1, 2, 3, 6, 11,
12), the roles of ?s and ?o swapped, `assert len(loops) < 2` (call 13),
the whole res2 query replaced by `[]`.  Mutants that stay green because
they are equivalent on every graph with a cycle: `*` instead of `+` in
res1 (a class on no cycle finds no loop), and a single step in only ONE of
the two patterns.
"""
from rdflib import Graph

from rdfeval.harness import run_pair, fixture_graph

_PREFIXES = """
@prefix brick: <https://brickschema.org/schema/Brick#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rec: <https://w3id.org/rec#> .
@prefix sosa: <http://www.w3.org/ns/sosa#> .
"""


class _OrderedGraph(Graph):
    """A graph whose query() yields its rows in a fixed order.

    The assertion message prints a SET of strings, and a set prints in an
    order that depends on the order of insertion.  No SPARQL engine promises
    an order among rows, and the two sides reach their rows through
    different calls, so left alone the two messages differ by chance (15 of
    40 PYTHONHASHSEED values in a trial).  Sorting the rows makes both
    sides insert in the same order; what the queries MATCH is untouched.
    """

    def query(self, *args, **kwargs):
        return sorted(super().query(*args, **kwargs),
                      key=lambda row: [repr(t) for t in row])


def _graph(turtle):
    """A fresh graph per side, built from Turtle text."""
    def build():
        g = _OrderedGraph().parse(data=_PREFIXES + turtle, format="turtle")
        return (g,), {}
    return build


def _fixture():
    from pathlib import Path
    path = Path(__file__).parent / "fixture.ttl"
    return lambda: ((fixture_graph(path),), {})


CALLS = [
    # 0
    _fixture(),
    # 1
    _graph("""
brick:A rdfs:subClassOf brick:B .
brick:B rdfs:subClassOf brick:A .
brick:D rdfs:subClassOf brick:A .
brick:E rdfs:subClassOf brick:D .
"""),
    # 2
    _graph("""
brick:A rdfs:subClassOf brick:B .
brick:B rdfs:subClassOf brick:C .
brick:C rdfs:subClassOf brick:A .
brick:A rdfs:subClassOf brick:C .
brick:S rdfs:subClassOf brick:S .
brick:T2 rdfs:subClassOf brick:S .
brick:Valve rdfs:subClassOf brick:Equipment .
"""),
    # 3
    _graph("""
brick:A rdfs:subClassOf brick:B .
brick:B rdfs:subClassOf brick:A .
brick:X rdfs:subClassOf brick:Y .
brick:Y rdfs:subClassOf brick:X .
brick:Equipment rdfs:subClassOf brick:Entity .
brick:Sensor rdfs:subClassOf brick:Equipment .
"""),
    # 4
    _graph("""
rec:P rdfs:subClassOf rec:Q .
rec:Q rdfs:subClassOf rec:P .
brick:Equipment rdfs:subClassOf brick:Entity .
"""),
    # 5
    _graph("""
rec:P rdfs:subClassOf rec:Q .
rec:Q rdfs:subClassOf rec:P .
brick:P rdfs:subClassOf brick:Q .
brick:Q rdfs:subClassOf brick:Entity .
"""),
    # 6
    _graph("""
brick:A rdfs:subClassOf brick:B .
brick:B rdfs:subClassOf brick:A .
rec:P rdfs:subClassOf rec:Q .
rec:Q rdfs:subClassOf rec:P .
"""),
    # 7
    _graph("""
brick:Equipment rdfs:subClassOf brick:Entity ,
    [ a owl:Restriction ; owl:onProperty brick:hasPart ;
      owl:someValuesFrom brick:Entity ] .
brick:Sensor rdfs:subClassOf brick:Equipment .
"""),
    # 8
    lambda: ((Graph(),), {}),
    # 9
    _graph("""
rec:P rdfs:subClassOf rec:Q .
rec:Q rdfs:subClassOf rec:P .
brick:P rdfs:subClassOf rec:Q .
"""),
    # 10
    _graph("""
rec:P rdfs:subClassOf rec:Q .
rec:Q rdfs:subClassOf rec:P .
rec:Q rdfs:subClassOf brick:P .
"""),
    # 11
    _graph("""
brick:X rdfs:subClassOf brick:Y .
brick:Y rdfs:subClassOf brick:X .
brick:Y rdfs:subClassOf brick:C .
brick:C rdfs:subClassOf brick:D .
brick:D rdfs:subClassOf brick:C .
brick:D rdfs:subClassOf brick:Z .
brick:Z rdfs:subClassOf brick:W .
brick:W rdfs:subClassOf brick:Z .
"""),
    # 12
    _graph("""
brick:A rdfs:subClassOf brick:B .
brick:B rdfs:subClassOf brick:C .
brick:C rdfs:subClassOf brick:D .
brick:D rdfs:subClassOf brick:A .
"""),
    # 13
    _graph("""
brick:S rdfs:subClassOf brick:S .
brick:T rdfs:subClassOf brick:S .
"""),
]


VERDICT = run_pair(
    __file__,
    entry='test_cycles',
    calls=CALLS,
)
