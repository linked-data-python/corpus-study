"""Validation driver for philbarker__TAP2SHACL__src_ap2shacl_ap2shaclConverter.py__AP2SHACLConverter_convert_shapes.

Establishes semantic equivalence of original.py and translated.ldpy.
Filled in during translation review; see rdfeval.harness for helpers.
"""
from rdfeval.harness import run_pair

# entry=None executes both modules and compares every rdflib Graph found in
# the module globals (plus captured stdout).  For function regions, set
# entry="<function name>" and provide the fixture arguments.
VERDICT = run_pair(
    __file__,
    entry='convert_shapes',
    calls=[]  # TODO: [(args, kwargs), ...] fixtures,
)
