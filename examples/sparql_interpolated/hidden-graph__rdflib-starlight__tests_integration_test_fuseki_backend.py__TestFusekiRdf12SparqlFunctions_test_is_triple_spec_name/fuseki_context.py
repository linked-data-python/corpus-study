# Context shim (see meta.json): the `sg_rdf12` fixture of
# hidden-graph/rdflib-starlight@b7973da2b5 tests/integration/test_fuseki_backend.py.
#
# The real fixture calls `_clear_graph()` (an HTTP POST of `CLEAR SILENT GRAPH`
# to the Fuseki update endpoint) and returns a `StarlightGraph` over a
# SPARQLUpdateStore on that Fuseki, `backend='rdf-1.2'`.  Both need what this
# machine does not have: a Fuseki 5.5+ on localhost:3030, and the `starlight`
# package (not installed; the repository's tests/conftest.py also imports
# `sparql1_2_to_rdf`).  So this stand-in does NOT reproduce the graph: it
# reproduces the constants and the `_clear_graph()` request of the fixture,
# verbatim, run at the first query, so that the region fails here exactly as
# the fixture does (a requests.ConnectionError on localhost:3030).  Identical for both representations.
import requests

FUSEKI_BASE = 'http://localhost:3030/starlight'
QUERY_URL = f'{FUSEKI_BASE}/query'
UPDATE_URL = f'{FUSEKI_BASE}/update'
GRAPH_URI = 'http://example.org/test-graph'


def _clear_graph():
    """Delete all triples from the test graph between tests."""
    requests.post(
        UPDATE_URL,
        data=f'CLEAR SILENT GRAPH <{GRAPH_URI}>',
        headers={'Content-Type': 'application/sparql-update'},
        auth=('admin', 'admin'),
        timeout=10,
    ).raise_for_status()


class SgRdf12:
    """Stand-in for the StarlightGraph the fixture yields.

    The real fixture runs `_clear_graph()` at SETUP; here it runs on the first
    `query()`, i.e. inside the region, so that the failure is the region's
    outcome (compared by the harness) and not an error in building its
    arguments."""

    def query(self, q):
        _clear_graph()      # first thing the real fixture does
        # (real: StarlightGraph(store=SPARQLUpdateStore(...), backend='rdf-1.2').query(q))
        raise NotImplementedError("needs the starlight package over a live Fuseki")
