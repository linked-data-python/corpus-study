# Extracted from OntoUML/ontouml-json2graph@982f12b9c4 : json2graph/modules/utils_graph.py
# region: rename_uriref_resource (lines 132-154, stratum remove)
# licence of the source repository: see meta.json
from rdflib import Graph, URIRef
LOGGER = initialize_logger()

def rename_uriref_resource(graph: Graph, old_resource: URIRef, new_resource: URIRef) -> None:
    """Rename a URIRef resource of an RDF graph by replacing it to a new one with a different name.

    :param graph: The RDF graph that contains the resource to be renamed.
    :type graph: Graph
    :param old_resource: The old resource to be replaced.
    :type old_resource: URIRef
    :param new_resource: The new resource to replace the old one.
    :type new_resource: URIRef
    :return: None
    """
    LOGGER.debug(f"Renaming {old_resource} to {new_resource}")

    for s, p, o in graph:
        if s == old_resource:
            graph.add((new_resource, p, o))
            graph.remove((old_resource, p, o))
        if p == old_resource:
            graph.add((s, new_resource, o))
            graph.remove((s, old_resource, o))
        if o == old_resource:
            graph.add((s, p, new_resource))
            graph.remove((s, p, old_resource))
