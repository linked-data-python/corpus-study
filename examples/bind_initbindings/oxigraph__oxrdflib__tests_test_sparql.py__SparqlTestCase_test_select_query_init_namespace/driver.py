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
"""
import unittest

from rdfeval.harness import run_pair

VERDICT = run_pair(
    __file__,
    entry='test_select_query_init_namespace',
    calls=[
        lambda: ((unittest.TestCase('assertEqual'),), {}),
    ],
)
