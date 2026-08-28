"""Validation driver for RDFLib__pyLODE__pylode_utils.py__rdf_obj_html__rdf_obj_single_html__restriction_html.

Establishes semantic equivalence of original.py and translated.ldpy.
Filled in during translation review; see rdfeval.harness for helpers.
"""
from rdfeval.harness import run_pair

# entry=None executes both modules and compares every rdflib Graph found in
# the module globals (plus captured stdout).  For function regions, set
# entry="<function name>" and provide the fixture arguments.
VERDICT = run_pair(
    __file__,
    entry='_restriction_html',
    calls=[]  # TODO: [(args, kwargs), ...] fixtures,
)
