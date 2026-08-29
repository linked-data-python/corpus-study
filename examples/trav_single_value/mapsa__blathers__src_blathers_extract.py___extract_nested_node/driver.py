"""Validation driver for mapsa__blathers__src_blathers_extract.py___extract_nested_node.

This region READS a graph, so the oracle is not isomorphism but the equality
of the values both versions produce from the same input graph (design record
corpus/405).  `fixture.ttl` is parsed fresh for each side.

`_extract_nested_node(g, node)` takes `node` as a second, external argument,
so a bare `fixture=` (which calls entry with the parsed graph as its sole
argument) is not enough here.  rdflib mints a fresh, unpredictable BNode
identifier on every parse, so `node` cannot be hardcoded either: each call
below parses its own fixture graph and resolves `node` from it via a named
anchor triple (`ex:ClassA/B/C ex:hasNested _:nN`), so the value handed to
`_extract_nested_node` is guaranteed to belong to the very graph it reads.

Two calls exercise the pattern the stratum (trav_single_value) is about:
  * with_comment    -- _:n1 (anchored by ex:ClassA) has an rdfs:comment: the
                       g.value()/m{ }.first() call finds a value among the
                       fixture's several rdfs:comment triples.
  * without_comment -- _:n2 (anchored by ex:ClassB) has no rdfs:comment: the
                       ZERO-solution case, where g.value() and m{ }.first()
                       must both answer None.
Neither call ever reads _:n3's or ex:Other's rdfs:comment/ex:label (the
neighbourhood in fixture.ttl).
"""
from rdflib import Namespace

from rdfeval.harness import fixture_graph, run_pair

FIXTURE = "fixture.ttl"
EX = Namespace("http://example.org/")


def with_comment():
    g = fixture_graph(FIXTURE)
    node = g.value(EX.ClassA, EX.hasNested)
    return ((g, node), {})


def without_comment():
    g = fixture_graph(FIXTURE)
    node = g.value(EX.ClassB, EX.hasNested)
    return ((g, node), {})


VERDICT = run_pair(
    __file__,
    entry='_extract_nested_node',
    fixture=FIXTURE,
    calls=[with_comment, without_comment],
    # ordered=True only if the region imposes an order (sorted, ORDER BY):
    # no store promises one, so results are compared as multisets. (Here the
    # region's own dict grouping is order-preserving and both m{ }/rdflib
    # iterate graph.triples() the same way for a fixed input, so this would
    # also pass with ordered=True -- left at the fixture default anyway,
    # since no store PROMISES an order.)
)
