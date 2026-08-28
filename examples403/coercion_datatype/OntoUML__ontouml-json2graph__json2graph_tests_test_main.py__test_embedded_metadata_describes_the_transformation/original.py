# Extracted from OntoUML/ontouml-json2graph@982f12b9c4 : json2graph/tests/test_main.py
# region: test_embedded_metadata_describes_the_transformation (lines 1786-1855, stratum coercion_datatype)
# licence of the source repository: see meta.json
import hashlib
import json
from pathlib import Path
from rdflib import RDF, RDFS, XSD, Graph, Literal, Namespace, URIRef
from ..modules.content_identity import create_content_uuid, resolve_base_uri
from ..modules.metadata import METADATA, _read_source_project_version
DCTERMS = Namespace("http://purl.org/dc/terms/")
PROV = Namespace("http://www.w3.org/ns/prov#")
ONTOUML_VOCABULARY_111 = URIRef("https://w3id.org/ontouml/vocabulary/v1.1.1")
IANA_MEDIA_TYPES = "https://www.iana.org/assignments/media-types/"

def test_embedded_metadata_describes_the_transformation(tmp_path: Path) -> None:
    """Verify the complete, opt-in embedded provenance profile."""
    input_file = write_cardinality_project(tmp_path, "0..1")

    result = run_metadata_cli(input_file, tmp_path, "embedded")

    assert result.returncode == 0, result.stderr
    output_file = tmp_path / "cardinality.ttl"
    output_graph = Graph().parse(output_file, format="turtle")
    output_artifact = get_output_artifact(output_graph)
    transformation = output_graph.value(output_artifact, PROV.wasGeneratedBy)

    assert (output_artifact, RDF.type, PROV.Entity) in output_graph
    assert (output_artifact, DCTERMS.title, Literal(output_file.name)) in output_graph
    assert (
        output_artifact,
        DCTERMS["format"],
        URIRef(IANA_MEDIA_TYPES + "text/turtle"),
    ) in output_graph
    assert (output_artifact, DCTERMS.conformsTo, ONTOUML_VOCABULARY_111) in output_graph
    assert (transformation, RDF.type, PROV.Activity) in output_graph

    generation_time = output_graph.value(output_artifact, PROV.generatedAtTime)
    assert generation_time.datatype == XSD.dateTime
    assert generation_time.toPython().utcoffset().total_seconds() == 0

    software_agents = set(output_graph.objects(transformation, PROV.wasAssociatedWith))
    assert len(software_agents) == 1
    software_agent = next(iter(software_agents))
    assert (software_agent, RDF.type, PROV.SoftwareAgent) in output_graph
    assert (software_agent, DCTERMS.title, Literal(METADATA["Name"])) in output_graph
    assert set(output_graph.objects(software_agent, DCTERMS.identifier)) == {
        Literal(f"{METADATA['Name']}/{METADATA['Version']}")
    }

    used_entities = set(output_graph.objects(transformation, PROV.used))
    source_artifact = next(
        entity for entity in used_entities if (entity, DCTERMS.title, Literal(input_file.name)) in output_graph
    )
    configuration_entity = next(entity for entity in used_entities if (entity, PROV.value, None) in output_graph)
    expected_digest = hashlib.sha256(input_file.read_bytes()).hexdigest()

    assert (source_artifact, RDF.type, PROV.Entity) in output_graph
    assert (source_artifact, DCTERMS.identifier, Literal(f"sha256:{expected_digest}")) in output_graph
    assert (
        source_artifact,
        DCTERMS["format"],
        URIRef(IANA_MEDIA_TYPES + "application/json"),
    ) in output_graph

    configuration = get_recorded_configuration(output_graph)
    expected_base_uri = resolve_base_uri(json.loads(input_file.read_text(encoding="utf-8")))
    assert configuration == {
        "append_content_hash": False,
        "base_uri": None,
        "correct": False,
        "effective_base_uri": expected_base_uri,
        "format": "ttl",
        "invalid_cardinality_policy": "preserve",
        "invalid_stereotype_policy": "preserve",
        "language": "",
        "model_only": False,
        "path_order_policy": "warn",
        "property_assignment_policy": "warn",
        "transformation_metadata": "embedded",
        "unresolved_model_element_policy": "omit",
    }
    assert (configuration_entity, DCTERMS["format"], URIRef(IANA_MEDIA_TYPES + "application/json")) in output_graph
    assert str(tmp_path) not in " ".join(str(value) for value in output_graph.objects(None, None))
    assert not (tmp_path / "cardinality.provenance.ttl").exists()
