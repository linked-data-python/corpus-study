# Extracted from KRR-Oxford/OWL2Vec-Star@e7cdc4d9c0 : owl2vec_star/lib/Onto_Projection.py
# region: OntologyProjection.__addInverseSubsumptionTriple__ (lines 768-769, stratum add_isolated)
# licence of the source repository: see meta.json
from rdflib import Graph, URIRef

def __addInverseSubsumptionTriple__(self, subclass_uri, superclass_uri):
    self.projection.add( (superclass_uri, URIRef("http://www.semanticweb.org/owl2vec#superClassOf"), subclass_uri) )
