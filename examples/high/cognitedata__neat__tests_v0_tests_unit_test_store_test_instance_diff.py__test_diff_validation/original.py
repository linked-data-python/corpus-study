# Extracted from cognitedata/neat@4042d3e96d : tests/v0/tests_unit/test_store/test_instance_diff.py
# region: test_diff_validation (lines 45-62, band high)
# licence of the source repository: see meta.json
import pytest
from rdflib import RDF, Literal, Namespace, URIRef
from cognite.neat._v0.core._issues.errors import NeatValueError
from cognite.neat._v0.core._store import NeatInstanceStore

def test_diff_validation() -> None:
    store = NeatInstanceStore.from_oxi_local_store()

    existing = URIRef("urn:test:exists")
    nonexistent = URIRef("urn:test:nonexistent")

    store._add_triples(
        [
            (URIRef("http://example.org/s"), RDF.type, URIRef("http://example.org/T")),
        ],
        named_graph=existing,
    )

    with pytest.raises(NeatValueError, match="Current named graph not found"):
        store.diff(nonexistent, existing)

    with pytest.raises(NeatValueError, match="New named graph not found"):
        store.diff(existing, nonexistent)
