# Extracted from OntoUML/ontouml-json2graph@982f12b9c4 : json2graph/tests/test_documentation.py
# region: assert_minimal_project_graph (lines 18-25, stratum trav_existence)
# licence of the source repository: see meta.json
from pathlib import Path
from rdflib import RDF, Graph, Namespace
ONTOUML = Namespace("https://w3id.org/ontouml#")

def assert_minimal_project_graph(graph_file: Path) -> None:
    """Assert that a serialized graph contains the canonical project's core resources."""
    graph = Graph()
    graph.parse(graph_file, format="turtle")

    assert any(graph.triples((None, RDF.type, ONTOUML.Project)))
    assert any(graph.triples((None, RDF.type, ONTOUML.Package)))
    assert any(graph.triples((None, RDF.type, ONTOUML.Class)))
