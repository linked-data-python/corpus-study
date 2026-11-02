"""Validation driver for LA3D__cogitarelink-solid__tests_test_interop_foundation.py__test_one_manager_per_container_assigns_a_container_tree.

The region is a test: it returns nothing when it passes, and RAISES
AssertionError (with a message naming the slug) when a read of its graph
comes back empty or wrong.  A driver that calls it once, on a graph where
every assertion holds, shows nothing (a hollow green).  What the region
computes is what its assertions read, so this driver gives it one graph that
satisfies all of them and, for each read, a graph that falsifies exactly that
read.  A raise is compared by type and message on both sides, so a
translation that is weaker, stricter or different on any read is caught.

Each graph is `fixture.ttl` parsed fresh for each side, then edited by a
function of this file (the same on both sides).  This departs from the
original, which only ever sees the repository's own files, and the departure
is justified by the fact that the original shows nothing otherwise.

CALLS
  0. the fixture as it is: every assertion holds
  1. no st:Manager at all: `next(g.subjects(...))` raises StopIteration
  2. a Manager without st:hasAssignment ("no st:hasAssignment")
  3. an assignment without st:assigns ("must be a ContainerTree")
  4. st:assigns names a tree that does not end in ContainerTree
  5. an assignment without st:manages (a decoy elsewhere keeps the pattern
     honest) ("must name the container")
  6. st:assigns and st:manages are literals: the assertions read str() and
     existence, so it passes
  7. the Manager is typed twice (st:Manager and another class): still passes
  8. the only st:Manager is a blank node: passes
"""
from rdflib import BNode, Literal, Namespace, RDF, URIRef

from rdfeval.harness import fixture_graph, run_pair

from pathlib import Path

HERE = Path(__file__).resolve().parent
EX = Namespace("http://example.org/")
ST = Namespace("http://www.w3.org/ns/shapetrees#")


def _graph(edit=None):
    def make():
        g = fixture_graph(HERE / "fixture.ttl")
        if edit is not None:
            edit(g)
        return (g,), {}
    return make


def _no_manager(g):
    g.remove((EX.mgr1, RDF.type, ST.Manager))


def _no_assignment(g):
    g.remove((EX.mgr1, ST.hasAssignment, None))


def _no_assigns(g):
    g.remove((EX.assign1, ST.assigns, None))


def _bad_tree(g):
    g.remove((EX.assign1, ST.assigns, None))
    g.add((EX.assign1, ST.assigns, URIRef("http://example.org/trees/WikiMemoryTree")))


def _no_manages(g):
    g.remove((EX.assign1, ST.manages, None))


def _literals(g):
    g.remove((EX.assign1, ST.assigns, None))
    g.remove((EX.assign1, ST.manages, None))
    g.add((EX.assign1, ST.assigns, Literal("a/b/ContainerTree")))
    g.add((EX.assign1, ST.manages, Literal("the container")))


def _typed_twice(g):
    g.add((EX.mgr1, RDF.type, EX.Other))


def _blank_manager(g):
    b = BNode()
    g.remove((EX.mgr1, RDF.type, ST.Manager))
    g.remove((EX.mgr1, ST.hasAssignment, EX.assign1))
    g.add((b, RDF.type, ST.Manager))
    g.add((b, ST.hasAssignment, EX.assign1))


VERDICT = run_pair(
    __file__,
    entry='test_one_manager_per_container_assigns_a_container_tree',
    calls=[
        _graph(),
        _graph(_no_manager),
        _graph(_no_assignment),
        _graph(_no_assigns),
        _graph(_bad_tree),
        _graph(_no_manages),
        _graph(_literals),
        _graph(_typed_twice),
        _graph(_blank_manager),
    ],
)
