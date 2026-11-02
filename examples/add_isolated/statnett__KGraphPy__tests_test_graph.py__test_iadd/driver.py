"""Validation driver for statnett__KGraphPy__tests_test_graph.py__test_iadd.

The region is a self-contained test: it builds two CIMGraphs, adds one
triple to the second, merges it into the first with `g += otherg` and
asserts on the result and on the provenance log.  It takes no argument,
returns None and prints nothing, so what the ORIGINAL can show is an
AssertionError.  The driver therefore calls it three times, patching
CIMGraph.__iadd__ (a real class of the pinned kgraphpy, imported through
context_shim) in the call callable, each time restored by the next:

CALL_1 -- unpatched: every assert passes (None).  A translation that wrote
          another triple, another identifier or another literal fails here
          while the original does not.
CALL_2 -- __iadd__ merges nothing (returns self): the original stops at the
          first assert (membership of <s1> <p1> "o" in pr.graph).
CALL_3 -- __iadd__ merges but with no provenance entry: the original stops
          later, at `len(entries) == 2`.
CALL_4 -- __iadd__ merges (with its provenance entry) the same subject and
          predicate but ANOTHER object: the original stops at the membership
          assert, which a translation with a widened pattern would pass.
A raise is compared like a value (type and message).
"""
import context_shim  # noqa: F401  (puts the pinned kgraphpy on sys.path)
from kgraphpy.graph import CIMGraph

from rdfeval.harness import run_pair

_IADD = CIMGraph.__iadd__


def _merges_nothing(self, other):
    return self


def _merges_without_provenance(self, other):
    from rdflib import Graph
    Graph.__iadd__(self, other)
    return self


def _merges_another_object(self, other):
    from rdflib import Graph, Literal
    changed = Graph(identifier=other.identifier)
    for s, p, _ in other:
        changed.add((s, p, Literal("another")))
    return _IADD(self, changed)


def _call_1():
    CIMGraph.__iadd__ = _IADD
    return (), {}


def _call_2():
    CIMGraph.__iadd__ = _merges_nothing
    return (), {}


def _call_3():
    CIMGraph.__iadd__ = _merges_without_provenance
    return (), {}


def _call_4():
    CIMGraph.__iadd__ = _merges_another_object
    return (), {}


VERDICT = run_pair(
    __file__,
    entry="test_iadd",
    calls=[_call_1, _call_2, _call_3, _call_4],
)
