# Extracted from Haigutus/triplets@7cf62970e8 : tests/test_shacl_report.py
# region: test_report_embeds_source_shape_definitions (lines 243-273, stratum trav_existence)
# licence of the source repository: see meta.json
import triplets  # noqa: F401 — registers the shacl accessor namespace
from triplets.validation.shacl_report import report_to_violations, violations_to_report_graph
DATA = pandas.DataFrame([
    ("d1", "Type", "Distribution", "i1"),
    ("d1", "label", "grid.xml", "i1"),
    ("b1", "Type", "Breaker", "i1"),
], columns=["ID", "KEY", "VALUE", "INSTANCE_ID"])

def test_report_embeds_source_shape_definitions(tmp_path):
    """sh:sourceShape is never an empty node: the violated shapes' defining
    triples (incl. the sh:in list) are embedded in the report, so the
    expected values are machine-recoverable from the report alone."""
    import rdflib
    from rdflib.collection import Collection

    shapes = tmp_path / "container_shapes.ttl"
    shapes.write_text("""
@prefix sh:  <http://www.w3.org/ns/shacl#> .
@prefix cim: <http://iec.ch/TC57/CIM100#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
cim:BreakerShape a sh:NodeShape ; sh:targetClass cim:Breaker ;
    sh:property [ sh:path ( cim:Equipment.EquipmentContainer rdf:type ) ;
                  sh:in ( cim:Bay cim:VoltageLevel ) ] .
""")
    data = DATA.copy()
    data.loc[len(data)] = ("b1", "Equipment.EquipmentContainer", "s1", "i1")
    data.loc[len(data)] = ("s1", "Type", "Substation", "i1")
    violations = triplets.validation.validate(data, shapes, engine="pandas")
    assert len(violations) == 1

    sh = rdflib.Namespace("http://www.w3.org/ns/shacl#")
    graph = violations_to_report_graph(violations)
    result = next(graph.subjects(rdflib.RDF.type, sh.ValidationResult))
    shape_node = graph.value(result, sh.sourceShape)
    assert graph.value(shape_node, sh.path) is not None            # not an empty node
    allowed = Collection(graph, graph.value(shape_node, sh["in"]))
    assert [str(item).split("#")[-1] for item in allowed] == ["Bay", "VoltageLevel"]
    # and the human-readable twin
    assert (violations["EXPECTED"] == "one of: Bay, VoltageLevel").all()
