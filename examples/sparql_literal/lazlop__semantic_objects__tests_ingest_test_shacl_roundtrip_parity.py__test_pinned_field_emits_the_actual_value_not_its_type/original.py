# Extracted from lazlop/semantic_objects@243c5efd8c : tests/ingest/test_shacl_roundtrip_parity.py
# region: test_pinned_field_emits_the_actual_value_not_its_type (lines 84-99, stratum sparql_literal)
# licence of the source repository: see meta.json
from rdflib import Graph
from semantic_objects.namespaces import bind_prefixes

def test_pinned_field_emits_the_actual_value_not_its_type():
    # Area.qk is pinned to `quantitykinds.Area` - the exporter used to read
    # `field_obj.type._get_iri()` (the *type annotation*, QuantityKind) instead of
    # the actually-pinned value, silently emitting the wrong sh:value.
    from semantic_objects.s223 import properties as hand_properties
    g = Graph()
    bind_prefixes(g)
    g.parse(data=hand_properties.Area.generate_rdf_class_definition(), format='turtle')
    assert bool(g.query("""
        PREFIX quantitykind: <http://qudt.org/vocab/quantitykind/>
        ASK { ?shape sh:path s223:hasQuantityKind ; sh:value quantitykind:Area . }
    """))
    assert not bool(g.query("""
        PREFIX quantitykind: <http://qudt.org/vocab/quantitykind/>
        ASK { ?shape sh:path s223:hasQuantityKind ; sh:value quantitykind:QuantityKind . }
    """))
