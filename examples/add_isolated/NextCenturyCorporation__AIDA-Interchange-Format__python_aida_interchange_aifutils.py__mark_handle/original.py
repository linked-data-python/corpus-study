# Extracted from NextCenturyCorporation/AIDA-Interchange-Format@1197e7adef : python/aida_interchange/aifutils.py
# region: mark_handle (lines 659-671, stratum add_isolated)
# licence of the source repository: see meta.json
from rdflib import RDF, XSD, BNode, Graph, Literal, URIRef
from aida_interchange.rdf_ontologies import interchange_ontology

def mark_handle(g, to_mark, handle) -> URIRef:
    """
    Add a handle to an existing resource

    :param rdflib.graph.Graph g: The underlying RDF model
    :param rdflib.term.URIRef to_mark: Reference to mark with a handle
    :param str handle: A string containing the handle
    :returns: The marked reference
    :rtype: rdflib.term.URIRef
    """
    if handle is not None:
        g.add((to_mark, interchange_ontology.handle, Literal(handle, datatype=XSD.string)))
    return to_mark
