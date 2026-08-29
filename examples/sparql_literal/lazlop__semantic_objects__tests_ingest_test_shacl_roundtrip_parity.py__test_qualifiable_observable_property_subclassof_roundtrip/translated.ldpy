# Extracted from lazlop/semantic_objects@243c5efd8c : tests/ingest/test_shacl_roundtrip_parity.py
# region: test_qualifiable_observable_property_subclassof_roundtrip (lines 60-65, stratum sparql_literal)
# licence of the source repository: see meta.json
from semantic_objects.s223._generated import entities, properties

def test_qualifiable_observable_property_subclassof_roundtrip():
    g = _shacl_graph(properties.QuantifiableObservableProperty)
    assert bool(g.query("""
        ASK { s223:QuantifiableObservableProperty rdfs:subClassOf ?p .
              FILTER(?p = s223:ObservableProperty || ?p = s223:QuantifiableProperty) }
    """))
