# Extracted from IndustryFusion/DigitalTwin@3b40088b88 : semantic-model/opcua/tests/test_libutils.py
# region: TestUtilityFunctions.setUp (lines 161-163, stratum ns_def_local)
# licence of the source repository: see meta.json
from rdflib import Graph, Namespace, URIRef, Literal, BNode

def setUp(self):
    # Initialize a base namespace for tests where needed.
    self.basens = Namespace("http://example.org/base/")
