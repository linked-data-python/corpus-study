# Extracted from IndustryFusion/DigitalTwin@3b40088b88 : semantic-model/opcua/tests/test_libshacl.py
# region: TestShaclCreateShaclPropertyName.setUp (lines 1018-1024, stratum ns_def_local)
# licence of the source repository: see meta.json
from rdflib import Graph, Namespace, URIRef, Literal, BNode
from lib.shacl import Shacl, Validation

def setUp(self):
    # Minimal setup for Shacl instance
    self.namespace_prefix = "http://example.org/"
    self.basens = Namespace("http://base/")
    self.opcuans = Namespace("http://opcuans/")
    self.data_graph = Graph()
    self.shacl = Shacl(self.data_graph, self.namespace_prefix, self.basens, self.opcuans)
