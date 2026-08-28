# Extracted from vital-ai/vital-graph@7fb3616c2d : test_scripts/data/reload_test_data.py
# region: reload_test_data (lines 229-236, stratum add_run_shared_subject)
# licence of the source repository: see meta.json
from rdflib import Graph, URIRef, Literal, Namespace, RDF, RDFS, XSD
TEST = Namespace("http://example.org/test#")

for entity in union_entities:
    test_graph.add((entity["uri"], RDF.type, TEST.UnionTestEntity))
    test_graph.add((entity["uri"], TEST.hasName, Literal(entity["name"])))
    test_graph.add((entity["uri"], TEST.hasCategory, Literal(entity["category"])))

    # Only add description if the entity has one (for UNION testing)
    if entity["hasDescription"]:
        test_graph.add((entity["uri"], TEST.hasDescription, Literal(entity["description"])))
