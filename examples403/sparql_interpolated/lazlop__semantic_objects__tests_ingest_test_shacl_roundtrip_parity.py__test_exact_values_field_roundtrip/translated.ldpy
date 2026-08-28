# Extracted from lazlop/semantic_objects@243c5efd8c : tests/ingest/test_shacl_roundtrip_parity.py
# region: test_exact_values_field_roundtrip (lines 102-113, stratum sparql_interpolated)
# licence of the source repository: see meta.json
from rdflib import Graph
from semantic_objects.namespaces import bind_prefixes

def test_exact_values_field_roundtrip():
    # ThresholdAlarm-style `exact_values` fields (e.g. Area_SP.aspects) used to
    # crash outright (Optional[list] has no _get_iri()). Each value should surface
    # as its own sh:hasValue property shape sharing the field's relation path.
    from semantic_objects.s223 import properties as hand_properties
    g = Graph()
    bind_prefixes(g)
    g.parse(data=hand_properties.Area_SP.generate_rdf_class_definition(), format='turtle')
    for value in ('Aspect-Setpoint', 'Aspect-Threshold', 'Domain-Occupancy'):
        assert bool(g.query(f"""
            ASK {{ ?shape sh:path s223:hasAspect ; sh:hasValue s223:{value} . }}
        """)), f"missing sh:hasValue for {value}"
