# Extracted from landrs-toolkit/PySOSA@1993668bd7 : PySOSA/Actuation.py
# region: Actuation.__init__ (lines 18-35, stratum add_run_shared_subject)
# licence of the source repository: see meta.json
from datetime import datetime
from rdflib import Graph, BNode, Literal, RDF, RDFS
from PySOSA import config as cfg
obsgraph = Graph()

def __init__(self,label,comment):
    """ instantiating Actuation object representing SOSA actuation
       Args:
           label, comment (literal): label and comment for the actuation
       Returns:
           actuation object: instantiated with actuation  properties
    """
    self.actuation_id = BNode()
    self.featureOfInterest = Literal
    self.label = Literal(label)
    self.comment = Literal(comment)
    self.dateTime = Literal(datetime)
    self.simpleResult = Literal

    obsgraph.add((self.actuation_id, RDF.type, cfg.sosa.Actuation))
    obsgraph.add((self.actuation_id, RDFS.comment, self.comment))
    obsgraph.add((self.actuation_id, RDFS.label, self.label))
    obsgraph.add((self.actuation_id, cfg.sosa.datetime, self.dateTime))
