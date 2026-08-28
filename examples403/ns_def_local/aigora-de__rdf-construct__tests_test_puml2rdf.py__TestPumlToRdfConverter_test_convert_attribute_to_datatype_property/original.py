# Extracted from aigora-de/rdf-construct@670e400ea4 : tests/test_puml2rdf.py
# region: TestPumlToRdfConverter.test_convert_attribute_to_datatype_property (lines 297-324, stratum ns_def_local)
# licence of the source repository: see meta.json
from rdflib import Graph, Namespace, RDF, RDFS, Literal
from rdflib.namespace import OWL, XSD
from rdf_construct.puml2rdf import (
    PlantUMLParser,
    PumlToRdfConverter,
    ConversionConfig,
    PumlModel,
    PumlClass,
    PumlAttribute,
    PumlRelationship,
    RelationshipType,
    validate_puml,
    validate_rdf,
    OntologyMerger,
)

def test_convert_attribute_to_datatype_property(self):
    """Test that attributes become datatype properties."""
    model = PumlModel(
        classes=[
            PumlClass(
                name="Building",
                attributes=[PumlAttribute(name="floorArea", datatype="decimal")],
            )
        ]
    )

    config = ConversionConfig(default_namespace="http://example.org/ont#")
    converter = PumlToRdfConverter(config)
    result = converter.convert(model)

    ns = Namespace("http://example.org/ont#")
    graph = result.graph

    # Check property type
    assert (ns.floorArea, RDF.type, OWL.DatatypeProperty) in graph

    # Check domain
    domains = list(graph.objects(ns.floorArea, RDFS.domain))
    assert ns.Building in domains

    # Check range
    ranges = list(graph.objects(ns.floorArea, RDFS.range))
    assert XSD.decimal in ranges
