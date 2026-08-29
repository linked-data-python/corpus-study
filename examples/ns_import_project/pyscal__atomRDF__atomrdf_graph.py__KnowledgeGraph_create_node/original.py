# Extracted from pyscal/atomRDF@c9b070e15f : atomrdf/graph.py
# region: KnowledgeGraph.create_node (lines 526-547, stratum ns_import_project)
# licence of the source repository: see meta.json
from rdflib import Graph, XSD, RDF, RDFS, BNode, URIRef
from atomrdf.namespace import (
    CMSO,
    PLDO,
    PODO,
    ASMO,
    PROV,
    CDCO,
    Literal,
)

def create_node(self, namestring, classtype, label=None):
    """
    Create a new node in the graph.

    Parameters
    ----------
    namestring : str
        The name of the node.
    classtype : Object from a given ontology
        The class type of the node.

    Returns
    -------
    URIRef
        The newly created node.

    """
    item = URIRef(namestring)
    self.add((item, RDF.type, classtype))
    if label is not None:
        self.add((item, RDFS.label, Literal(_clean_string(label))))
    return item
