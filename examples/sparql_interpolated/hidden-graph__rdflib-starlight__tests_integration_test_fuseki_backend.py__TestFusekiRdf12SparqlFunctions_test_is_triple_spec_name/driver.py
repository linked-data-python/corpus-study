"""Validation driver for hidden-graph__rdflib-starlight__tests_integration_test_fuseki_backend.py__TestFusekiRdf12SparqlFunctions_test_is_triple_spec_name.

EXCLUDED (see meta.json): the test is an integration test of a StarlightGraph
over a live Apache Jena Fuseki (5.5+), and asserts on the answer of Fuseki's
engine to `isTRIPLE(TRIPLE(<a>, <b>, <c>))` -- SPARQL 1.2 functions that no
rdflib parser knows.  There is no server here, so neither side can produce the
value the assertion is about.

The driver calls the region with the stand-in fixture of fuseki_context.py,
whose first `query()` does what the real fixture does first (`_clear_graph()`,
an HTTP POST to localhost:3030).  On both sides the call then RAISES the same
requests.ConnectionError ("Connection refused"), which the harness compares as
an outcome; it is the exact error recorded in meta.json, and the reason the
pair stays a draft.  A green here proves nothing about the translation.
"""
from fuseki_context import SgRdf12
from rdfeval.harness import run_pair

VERDICT = run_pair(
    __file__,
    entry='test_is_triple_spec_name',
    calls=[
        lambda: ((None, SgRdf12()), {}),   # self is unused in the region body
    ],
)
