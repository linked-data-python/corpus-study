# Extracted from CatholicOS/ontokit-api@23680a4d04 : tests/unit/test_ontology_service.py
# region: graph_untagged_label (lines 49-55, stratum add_run_shared_subject)
# licence of the source repository: see meta.json
import pytest
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import OWL, RDF, RDFS, SKOS
EX = Namespace("http://example.org/")

@pytest.fixture
def graph_untagged_label() -> Graph:
    """Create an RDF graph with a label that has no language tag."""
    g = Graph()
    g.add((EX.Widget, RDF.type, OWL.Class))
    g.add((EX.Widget, RDFS.label, Literal("Widget")))
    return g
