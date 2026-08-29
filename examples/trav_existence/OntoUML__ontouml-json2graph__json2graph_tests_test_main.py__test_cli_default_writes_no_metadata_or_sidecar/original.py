# Extracted from OntoUML/ontouml-json2graph@982f12b9c4 : json2graph/tests/test_main.py
# region: test_cli_default_writes_no_metadata_or_sidecar (lines 1774-1783, stratum trav_existence)
# licence of the source repository: see meta.json
from pathlib import Path
from rdflib import RDF, RDFS, XSD, Graph, Literal, Namespace, URIRef
PROV = Namespace("http://www.w3.org/ns/prov#")

def test_cli_default_writes_no_metadata_or_sidecar(tmp_path: Path) -> None:
    """Verify that omitting the new CLI option preserves metadata-free output."""
    input_file = write_cardinality_project(tmp_path, "0..1")

    result = run_metadata_cli(input_file, tmp_path)

    assert result.returncode == 0, result.stderr
    output_graph = Graph().parse(tmp_path / "cardinality.ttl", format="turtle")
    assert not any(output_graph.triples((None, RDF.type, PROV.Entity)))
    assert not (tmp_path / "cardinality.provenance.ttl").exists()
