# Extracted from jupyter-naas/abi@3fb7f5304d : libs/naas-abi-marketplace/naas_abi_marketplace/domains/operations/modules/ontology_engineer/workflows/EntityResolutionWorkflow.py
# region: EntityResolutionWorkflow.get_keys_for_class (lines 210-240, stratum bind_initbindings)
# licence of the source repository: see meta.json
from typing import Annotated, List, Optional, Set, Tuple, cast
from shim import logger
from rdflib import RDFS, Graph, Literal, Node, URIRef
from rdflib.collection import Collection
from rdflib.query import ResultRow

def get_keys_for_class(
    self, graph: Graph, class_uri: URIRef
) -> Optional[List[Node]]:
    """
    Get the keys (owl:hasKey) for a specific class.
    :param graph: The RDF graph to query.
    :param class_uri: The URI of the class (as string or URIRef).
    :return: A list of keys (Node objects, typically URIRef) if the class has keys, None otherwise.
    """
    for list_node in graph.objects(class_uri, URIRef("http://www.w3.org/2002/07/owl#hasKey")):
        # Extract all keys from the RDF list
        try:
            return list(Collection(graph, list_node))
        except Exception as e:
            logger.warning(f"{class_uri} - Error extracting keys: {e}")
            return None

    return None
