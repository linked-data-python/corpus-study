# Context shim (see meta.json): stand-in for the `get_ontology_path` pytest
# fixture that EMMC-ASBL/tripper's own test suite (tests/conftest.py)
# injects into test_backend_rdflib_graph. The real fixture resolves a name
# like "family" against tripper's bundled tests/testdata/ ontologies, which
# this corpus does not vendor. Here it always resolves to fixture.ttl
# (the minimal family ontology written for this region), which is the only
# name the region ever asks for. Used only by driver.py, on both sides.
from pathlib import Path

_HERE = Path(__file__).resolve().parent


def get_ontology_path(name: str) -> Path:
    return _HERE / "fixture.ttl"
