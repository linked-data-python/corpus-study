# Extracted from landrs-toolkit/PySOSA@1993668bd7 : PySOSA/Observation.py
# region: Observation.__init__ (lines 20-37, band high)
# licence of the source repository: see meta.json
from datetime import datetime
from rdflib import Graph, BNode, Literal, RDF, RDFS
from PySOSA import config as cfg
obsgraph = Graph()

def __init__(self, label, comment):
    """ instantiating Observation object
         Args:
             label, comment (literal): label and comment for the observation carried out
         Returns:
             an observation: initialized with observation_id, FOI, dateTime, simple result, label and comment
      """
    self.observation_id = BNode()
    self.dateTime = Literal(datetime)
    self.featureOfInterest = Literal
    self.comment = Literal(comment)
    self.label = Literal(label)
    self.simpleResult = Literal

    obsgraph.add((self.observation_id, RDF.type , cfg.sosa.Observation))
    obsgraph.add((self.observation_id, RDFS.comment, self.comment))
    obsgraph.add((self.observation_id, RDFS.label, self.label))
    obsgraph.add((self.observation_id, cfg.sosa.dateTime, self.dateTime))
