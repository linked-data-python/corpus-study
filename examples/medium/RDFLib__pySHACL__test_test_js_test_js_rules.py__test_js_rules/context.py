# Context shim (see meta.json): pySHACL itself (and the pyduktape2 JS engine
# the `js=True` option needs) is not installed in the evaluation environment,
# and the JS library the shapes point at lives in the pySHACL checkout.
# `validate` below is a RECORDING DOUBLE: it keeps the graphs it was handed
# and reports the non-conformance the original test asserts.
# Used IDENTICALLY by original.py and translated.ldpy.
# Provenance: RDFLib/pySHACL@469cca7a22, test/test_js/test_js_rules.py.
from rdflib import Graph

_LAST = []


def validate(data_graph, shacl_graph=None, **kwargs):
    _LAST[:] = [data_graph, shacl_graph, kwargs]
    return False, Graph(), "Validation Report\nConforms: False\n"


def last_validate_call():
    """(data graph, shapes graph) of the most recent validate() call."""
    return _LAST[0], _LAST[1]
