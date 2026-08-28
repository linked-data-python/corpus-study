# Extracted from landrs-toolkit/PySOSA@1993668bd7 : PySOSA/FeatureOfInterest.py
# region: FeatureOfInterest.get_uri (lines 28-35, band high)
# licence of the source repository: see meta.json
from rdflib import Graph, BNode, Literal, RDF, RDFS
obsgraph = Graph()

def get_uri(self):
    """
    get uri of a feature of interest
    """
    return self.feature_of_interest_id
    obsgraph.add((self.feature_of_interest_id, RDF.type, sosa.FeatureOfInterest))
    obsgraph.add((self.feature_of_interest_id, RDFS.comment, self.comment))
    obsgraph.add((self.feature_of_interest_id, RDFS.label, self.label))
