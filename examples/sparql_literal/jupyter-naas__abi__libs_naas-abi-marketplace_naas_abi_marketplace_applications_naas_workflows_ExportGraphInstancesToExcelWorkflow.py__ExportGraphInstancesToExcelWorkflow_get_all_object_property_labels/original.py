# Extracted from jupyter-naas/abi@3fb7f5304d : libs/naas-abi-marketplace/naas_abi_marketplace/applications/naas/workflows/ExportGraphInstancesToExcelWorkflow.py
# region: ExportGraphInstancesToExcelWorkflow.get_all_object_property_labels (lines 136-157, stratum sparql_literal)
# licence of the source repository: see meta.json
from naas_abi_core import logger
from rdflib import RDF, Graph, URIRef, query

def get_all_object_property_labels(self, graph: Graph) -> dict[str, str]:
    """Get object property label from URI.
    If the object property URI is not in the prefixes, return the last part of the URI."""

    sparql_query = """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    SELECT ?uri ?label
    WHERE {
        ?uri rdf:type owl:ObjectProperty ;
             rdfs:label ?label .
    }
    """
    results = graph.query(sparql_query)
    object_property_labels: dict = {}
    for row in results:
        assert isinstance(row, query.ResultRow)
        if row[0] is not None and row[1] is not None:
            object_property_labels[str(row[0])] = str(row[1])
    logger.info(f"Found {len(object_property_labels)} object properties.")
    return object_property_labels
