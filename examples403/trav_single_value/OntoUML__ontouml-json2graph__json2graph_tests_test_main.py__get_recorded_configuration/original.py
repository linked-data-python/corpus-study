# Extracted from OntoUML/ontouml-json2graph@982f12b9c4 : json2graph/tests/test_main.py
# region: get_recorded_configuration (lines 1744-1753, stratum trav_single_value)
# licence of the source repository: see meta.json
import json
from rdflib import RDF, RDFS, XSD, Graph, Literal, Namespace, URIRef
PROV = Namespace("http://www.w3.org/ns/prov#")

def get_recorded_configuration(metadata_graph: Graph) -> dict[str, object]:
    """Return the canonical JSON configuration used by the transformation."""
    transformation = metadata_graph.value(get_output_artifact(metadata_graph), PROV.wasGeneratedBy)
    configuration_entities = [
        entity
        for entity in metadata_graph.objects(transformation, PROV.used)
        if (entity, PROV.value, None) in metadata_graph
    ]
    assert len(configuration_entities) == 1
    return json.loads(str(metadata_graph.value(configuration_entities[0], PROV.value)))
