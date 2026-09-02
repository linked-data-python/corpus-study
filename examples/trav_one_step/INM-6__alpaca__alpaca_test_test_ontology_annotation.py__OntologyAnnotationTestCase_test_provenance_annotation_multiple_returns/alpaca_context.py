# Context shim (see meta.json): subset of alpaca/test/test_ontology_annotation.py
# from INM-6/alpaca@2b8dd34fc6f9a4c1ed2004e014b3ed9495eda1ba -- the test
# fixtures (EXAMPLE_NS, InputObject, OutputObject, process_multiple) that
# the extracted method (OntologyAnnotationTestCase.test_provenance_annotation_multiple_returns)
# uses but does not define itself: they live at module scope in the same
# test file, outside the extracted method's own line range (539-631).
# Reproduced verbatim (lines 1-13, 20-33, 68-77 of the source file).
# Identical bindings for both representations.
from rdflib import Namespace

from alpaca import Provenance

# Ontology namespace definition used for the tests
EXAMPLE_NS = {'ontology': "http://example.org/ontology#"}

# The namespace OntologyAnnotationTestCase.setUpClass binds to cls.ONTOLOGY
# (cls.ONTOLOGY = Namespace(EXAMPLE_NS['ontology'])); driver.py supplies it
# as the `self` argument's .ONTOLOGY attribute, same value.
ONTOLOGY = Namespace(EXAMPLE_NS['ontology'])


##############################
# Test objects to be annotated
##############################

class InputObject:
    __ontology__ = {
        "data_object": "ontology:InputObject",
        "namespaces": EXAMPLE_NS}


class OutputObject:
    __ontology__ = {
        "data_object": "ontology:OutputObject",
        "attributes": {'name': "ontology:Attribute"},
        "namespaces": EXAMPLE_NS}

    def __init__(self, name, channel):
        self.name = name
        self.channel = channel


#######################################################
# Test functions to be annotated and provenance tracked
#######################################################

@Provenance(inputs=['input'])
def process_multiple(input, param_1):
    return "not_annotated", OutputObject("SpikeTrain#2", 34)

process_multiple.__wrapped__.__ontology__ = {
    "function": "ontology:ProcessFunctionMultiple",
    "namespaces": EXAMPLE_NS,
    "arguments": {'param_1': "ontology:Parameter"},
    "returns": {1: "ontology:ProcessedDataMultiple"}
}
