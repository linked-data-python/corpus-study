"""Driver for ArangoDB-Community__ArangoRDF__tests_test_main.py__test_rpt_case_12_2.

EXCLUDED (see meta.json): the region needs a live ArangoDB.  It is a test of
the ArangoRDF round trip: `adbrdf.rdf_to_arangodb_by_rpt(...)` loads the case
into an ArangoDB server, the collections are checked, and
`adbrdf.arangodb_graph_to_rdf(...)` reads it back into `rdf_graph_2`, on which
the region makes its existence checks (the `trav_existence` part).  Nothing of
that runs here:

* `from .conftest import ...` is a relative import (no parent package once the
  region is extracted): ImportError "attempted relative import with no known
  parent package";
* `python-arango` / `arango_rdf` are not installed (ModuleNotFoundError: No
  module named 'arango'), and the repository's conftest connects, when pytest
  configures, to http://localhost:8529 (`ArangoClient(...).db(..., verify=True)`
  fails with no server there).

`fixture.ttl` is the case file of the repository (tests/data/rdf/cases/12_2.ttl),
the `rdf_graph` argument.  The pair was proved once outside the study tree
against stand-ins for `adbrdf`, `db` and the collections (the round trip
returning the case unchanged, then with the owner triple dropped, the
rdf:Statement typing dropped, the object replaced, an extra triple): equivalent
on those five calls.  The third shows why translated.ldpy writes
`... .first() or ANY`: `rdf_graph_2.value(...)` is None when no statement is
found and `(None, p, o) in g` then matches any subject, whereas an interpolated
None raises TypeError in m{ }.
"""
from rdfeval.harness import fixture_graph, run_pair
from pathlib import Path

HERE = Path(__file__).resolve().parent

VERDICT = run_pair(
    __file__,
    entry='test_rpt_case_12_2',
    fixture="fixture.ttl",
    calls=[lambda: (("Case_12_2_RPT", fixture_graph(HERE / "fixture.ttl")), {})],
)
