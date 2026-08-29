# Extracted from NextCenturyCorporation/AIDA-Interchange-Format@1197e7adef : python/aida_interchange/aifutils.py
# region: mark_name (lines 60-69, stratum coercion_datatype)
# licence of the source repository: see meta.json
from rdflib import RDF, XSD, BNode, Graph, Literal, URIRef
from aida_interchange.rdf_ontologies import interchange_ontology

def mark_name(g, entity, name):
    """
    Mark [entity] as having the specified [name].

    :param rdflib.graph.Graph g: The underlying RDF model
    :param rdflib.term.URIRef entity: The resource to mark on
    :param str name: The string name with which to mark the specified resource
    """
    g.add((entity, interchange_ontology.hasName,
           Literal(name, datatype=XSD.string)))
