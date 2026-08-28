# Extracted from cognitedata/neat@4042d3e96d : tests/v0/tests_unit/test_store/test_instance_diff.py
# region: test_diff_validation (lines 45-62, band high)
# licence of the source repository: see meta.json
import pytest
from rdflib import RDF, Literal, Namespace, URIRef
from neat_context import NeatValueError
from neat_context import NeatInstanceStore

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

# --- demo harness, added IDENTICALLY to original.py and translated.ldpy ----
# The region's own assertions only observe named-graph existence; running it
# here and exposing the store contents as a module-level Graph lets the
# driver compare the triple it wrote as well.
from neat_context import last_store_triples

test_diff_validation()
recorded = last_store_triples()
