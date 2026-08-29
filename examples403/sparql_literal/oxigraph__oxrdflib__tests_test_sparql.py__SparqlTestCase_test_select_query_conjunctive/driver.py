"""Validation driver for oxigraph__oxrdflib__tests_test_sparql.py__SparqlTestCase_test_select_query_conjunctive.

EXCLUDED (see meta.json). This region does not read an external graph -- it
builds its own tiny graph in-line (one `.add`) against a store backed by
`ConjunctiveGraph("Oxigraph")` and asserts on the SELECT result, so the
generic `oracle:values`/`fixture=` contract this file was scaffolded for
does not apply: the entry point takes `self` (a unittest.TestCase-shaped
stub for `self.assertEqual`), not a graph. A plain `unittest.TestCase()`
instance stands in for `self` -- `assertEqual` behaves identically and
raises AssertionError on mismatch either way.

The real, irreducible blocker is `ConjunctiveGraph("Oxigraph")`: the
"Oxigraph" rdflib store plugin is registered by the `oxrdflib` package (this
region's OWN library under test, backed by the native `pyoxigraph`
extension), and neither is installed here (`import oxrdflib` /
`import pyoxigraph` -> ModuleNotFoundError, checked directly). rdflib raises
`PluginException: No plugin registered for (Oxigraph, ...)` at that line, on
*both* sides identically, before the `s{ }`/`+{ }` rewrite under study is
ever reached. Vendoring oxrdflib's native store would mean reproducing the
system under test, not restoring a broken binding, so no context shim
applies (AGENT_BATCH.md: "n'inventez pas de logique").

The `s{ }`/`+{ }` rewrite itself was checked independently, outside this
harness (see translation_notes in meta.json): swapping in a plain in-memory
`ConjunctiveGraph()` (rdflib's default store, standing in only for the
unavailable "Oxigraph" one -- never done here, so as not to substitute a
different SPARQL engine into the actual pilot) makes both the original
`g.add(...)` / `g.query("SELECT ...")` code and the `@graph g` / `+{ }` /
`s{ SELECT ... }.execute()` translation produce byte-identical
`serialize(format="json")` output, equal to the literal the test asserts.
"""
import unittest

from rdfeval.harness import run_pair


def _self():
    return ((unittest.TestCase(),), {})


VERDICT = run_pair(
    __file__,
    entry='test_select_query_conjunctive',
    calls=[_self],
)
