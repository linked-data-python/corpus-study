"""Validation driver for jupyter-naas__abi__libs_naas-abi-core_naas_abi_core_utils_validate_bfo_ontology.py__check_license.

Establishes semantic equivalence of original.py and translated.ldpy.
Filled in during translation review; see rdfeval.harness for helpers.
"""
from rdfeval.harness import run_pair

# entry=None executes both modules and compares every rdflib Graph found in
# the module globals (plus captured stdout).  For function regions, set
# entry="<function name>" and provide the fixture arguments.
VERDICT = run_pair(
    __file__,
    entry='check_license',
    calls=[]  # TODO: [(args, kwargs), ...] fixtures,
)
