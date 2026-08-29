# Extracted from IndustryFusion/DigitalTwin@3b40088b88 : semantic-model/opcua/lib/entity.py
# region: Entity.add_instancetype (lines 88-95, stratum add_run_shared_subject)
# licence of the source repository: see meta.json
from rdflib import Graph, Namespace, Literal, URIRef, BNode
from rdflib.namespace import OWL, RDF, RDFS

def add_instancetype(self, instancetype, attributename):
    if not isinstance(attributename, URIRef):
        iri = self.entity_namespace[attributename]
    else:
        iri = attributename
    self.e.add((iri, RDF.type, OWL.ObjectProperty))
    self.e.add((iri, RDFS.domain, URIRef(instancetype)))
    self.e.add((iri, RDF.type, OWL.NamedIndividual))
