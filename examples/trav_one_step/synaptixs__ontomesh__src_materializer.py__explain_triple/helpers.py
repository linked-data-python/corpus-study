# Context shim (see meta.json): subset of src/materializer.py from
# synaptixs/ontomesh@f771c8c4ee, so the region executes outside the module
# (it calls _parse_term, defined just below the region in the source file).
# Identical bindings for both representations.
from rdflib import Literal, URIRef


def _parse_term(text: str):
    text = text.strip()
    if text.startswith('"'):
        end = text.rfind('"')
        return Literal(text[1:end])
    if text.startswith("<") and text.endswith(">"):
        return URIRef(text[1:-1])
    return URIRef(text)
