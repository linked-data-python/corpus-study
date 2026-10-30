"""Validation driver for oxigraph__oxrdflib__tests_test_sparql.py__SparqlTestCase_test_select_query_init_namespace.

This region READS a graph in form (`g.query(...)`), but its WHERE clause is
empty (`WHERE {}`) -- an empty basic graph pattern matches exactly once,
unconditionally, with no dependency on any triple in `g`. There is no
"several solutions"/"zero solutions"/"non-matching neighbourhood" to put in
a fixture: nothing in this query reads graph data at all, so `fixture.ttl`
stays a documented stub rather than fabricated triples that the query would
never look at (see fixture.ttl and meta.json).

`test_select_query_init_namespace(self)` takes the test's `self`, not a
graph -- `self.assertEqual(...)` is the region's own oracle: it already
raises AssertionError on a mismatch, on both sides, against the same
hard-coded expected JSON copied verbatim into both original.py and
translated.ldpy. `self` is a plain `unittest.TestCase` instance here:
`SparqlTestCase(unittest.TestCase)` in the source file defines no setUp of
its own (see meta.json). Two such instances, built the same way for each
side, compare equal via `TestCase.__eq__` (same class, same
`_testMethodName`), so the harness's generic per-argument comparison does
not need special-casing.

Which engine answers.  The region is a test of oxrdflib's Oxigraph store:
what it checks is that the STORE's own SPARQL engine (pyoxigraph) honours
`initNs`.  `rdflib.Graph.query` first offers the query to the store, and
silently falls back to rdflib's own evaluator when the store raises
NotImplementedError -- which `OxigraphStore.query` does for an already
parsed `Query` object (oxrdflib/store.py).  The assertion alone cannot see
which engine produced the row, so `OxigraphStore.query` is wrapped below by
a recorder, installed once for the whole process and therefore identical
for both sides: it prints whether the store answered or declined.  The
harness compares each call's stdout, so a side whose query never reaches
pyoxigraph -- a test that no longer tests the store -- is a difference.
"""
import unittest

from oxrdflib.store import OxigraphStore

from rdfeval.harness import run_pair

_store_query = OxigraphStore.query


def _recording_query(self, query, *args, **kwargs):
    try:
        result = _store_query(self, query, *args, **kwargs)
    except NotImplementedError as e:
        print(f"OxigraphStore.query declined: {e}")
        raise
    print("OxigraphStore.query answered")
    return result


OxigraphStore.query = _recording_query

VERDICT = run_pair(
    __file__,
    entry='test_select_query_init_namespace',
    calls=[
        lambda: ((unittest.TestCase('assertEqual'),), {}),
    ],
)
