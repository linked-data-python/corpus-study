# Extracted from dtai-kg/SCOOP@40c6fc0420 : SCOOP/shape_integration_priority.py
# region: ShapeIntegrationPriority.__init__ (lines 11-22, stratum ns_def_local)
# licence of the source repository: see meta.json
from typing import List, Dict
from rdflib import Graph, Namespace, URIRef, Literal, BNode
import random

def __init__(self, shapes: List, output: str):
    self.shaclNS = Namespace('http://www.w3.org/ns/shacl#')
    self.rdfSyntax = Namespace(
        'http://www.w3.org/1999/02/22-rdf-syntax-ns#')
    self.targetDeclarationNS = [self.shaclNS.targetClass, self.shaclNS.targetNode, self.shaclNS.targetSubjectsOf, self.shaclNS.targetObjectsOf]
    self.propertyPathNS = [self.shaclNS.path]
    self.shapes = shapes
    self.output = output
    self.SHACL = Graph()

    self.integrated_identifier = []
    self.random_number = [random.randint(1000, 9999) for i in range(1000)]
