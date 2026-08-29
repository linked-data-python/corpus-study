# Extracted from dfriedenberger/obse@43d0cc1776 : obse/graphwrapper.py
# region: GraphWrapper.add_labeled_instance (lines 41-47, stratum add_run_shared_subject)
# licence of the source repository: see meta.json
from rdflib import Graph, Literal, RDF, RDFS, URIRef, BNode, Seq
from rdflib.namespace import XSD

def add_labeled_instance(self, rdf_type: URIRef, name: str, unique_name: str = None) -> URIRef:
    if unique_name is None:
        unique_name = name
    rdf_object = self.create_ref(rdf_type, unique_name)
    self.graph.add((rdf_object, RDF.type, rdf_type))
    self.graph.add((rdf_object, RDFS.label, Literal(name, datatype=XSD.string)))
    return rdf_object
