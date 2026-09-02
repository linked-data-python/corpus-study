# Context shim (see meta.json): subset of json2graph/modules/arguments.py
# (the ARGUMENTS dict) and json2graph/modules/utils_graph.py (ontouml_ref),
# from OntoUML/ontouml-json2graph@982f12b9c4, so the region executes outside
# the package. Identical bindings for both representations.
from rdflib import URIRef

ARGUMENTS = {"base_uri": "https://example.org#"}


def ontouml_ref(entity: str) -> URIRef:
    return URIRef("https://w3id.org/ontouml#" + entity)
