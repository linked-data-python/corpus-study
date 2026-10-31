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
  * two_comments    -- _:n4 (anchored by ex:ClassD) has TWO rdfs:comment
                       values (added at repair, 2026-10-31): the two-solution
                       case, where g.value() (any=True) and m{ }.first() must
                       return the same one, and where .one() would raise.  It
                       also carries falsy values (ex:label "" and ex:weight 0)
                       that the predicate_objects loop must keep as "" and "0".
                       So the comment site is exercised with zero (n2), one
                       (n1) and two (n4) solutions.
No call ever reads _:n3's or ex:Other's rdfs:comment/ex:label (the
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


def two_comments():
    g = fixture_graph(FIXTURE)
    node = g.value(EX.ClassD, EX.hasNested)
    return ((g, node), {})


VERDICT = run_pair(
    __file__,
    entry='_extract_nested_node',
    fixture=FIXTURE,
    calls=[with_comment, without_comment, two_comments],
    # ordered=True only if the region imposes an order (sorted, ORDER BY):
    # no store promises one, so results are compared as multisets. (Here the
    # region's own dict grouping is order-preserving and both m{ }/rdflib
    # iterate graph.triples() the same way for a fixed input, so this would
    # also pass with ordered=True -- left at the fixture default anyway,
    # since no store PROMISES an order.)
)
