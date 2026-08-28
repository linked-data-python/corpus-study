# Extracted from IndustryFusion/DigitalTwin@3b40088b88 : semantic-model/opcua/lib/entity.py
# region: Entity.__init__ (lines 72-80, stratum ns_import_project)
# licence of the source repository: see meta.json
from rdflib import Graph, Namespace, Literal, URIRef, BNode
from lib.utils import NGSILD, collection_to_list, calculate_array_dimensions

def __init__(self, namespace_prefix, basens, opcuans):
    self.e = Graph()
    self.basens = basens
    self.opcuans = opcuans
    self.entity_namespace = Namespace(f'{namespace_prefix}entity/')
    self.e.bind('uaentity', self.entity_namespace)
    self.ngsildns = NGSILD
    self.e.bind('ngsi-ld', self.ngsildns)
    self.types = []
