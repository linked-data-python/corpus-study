# Extracted from dtai-kg/SCOOP@40c6fc0420 : SCOOP/shape_generator/xsd2shacl/src/XSDtoSHACL.py
# region: XSDtoSHACL.__init__ (lines 12-31, stratum ns_def_local)
# licence of the source repository: see meta.json
import rdflib
from rdflib import Graph, Literal, BNode, Namespace, RDF, URIRef
from .utils import recursiceCheck, built_in_types

def __init__(self):
    """
    Initialize the XSDtoSHACL class
    """
    self.shaclNS = rdflib.Namespace('http://www.w3.org/ns/shacl#')
    self.rdfSyntax = rdflib.Namespace('http://www.w3.org/1999/02/22-rdf-syntax-ns#')
    self.xsdNS = rdflib.Namespace('http://www.w3.org/2001/XMLSchema#')
    self.xsdTargetNS = rdflib.Namespace('http://example.com/')
    self.NS = rdflib.Namespace('http://example.com/')
    self.type_list = built_in_types()
    self.xsdNSdict = dict()
    self.SHACL = Graph()
    self.shapes = []
    self.extensionShapes = []
    self.extension = False
    self.enumerationShapes = []
    self.choiceShapes = []
    self.order_list = []
    self.backUp = None
    self.processed_files = []
