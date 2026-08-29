"""Validation driver for OntoUML__ontouml-json2graph__json2graph_decoder_decode_obj_package.py__set_package_containsmodelelement_modelelement.

Establishes semantic equivalence of original.py and translated.ldpy.
Filled in during translation review; see rdfeval.harness for helpers.
"""
from rdfeval.harness import run_pair

# entry=None executes both modules and compares every rdflib Graph found in
# the module globals (plus captured stdout).  For function regions, set
# entry="<function name>" and provide the fixture arguments.
VERDICT = run_pair(
    __file__,
    entry='set_package_containsmodelelement_modelelement',
    calls=[]  # TODO: [(args, kwargs), ...] fixtures,
)
