"""Validation driver for calipho-sib__nextprot-scripts__src_polish-rdf_pylode_pyLODE-2.13.2_pylode_profiles_base.py__BaseProfile__make_schemaorg_metadata.

Establishes semantic equivalence of original.py and translated.ldpy.
Filled in during translation review; see rdfeval.harness for helpers.
"""
from rdfeval.harness import run_pair

# entry=None executes both modules and compares every rdflib Graph found in
# the module globals (plus captured stdout).  For function regions, set
# entry="<function name>" and provide the fixture arguments.
VERDICT = run_pair(
    __file__,
    entry='_make_schemaorg_metadata',
    calls=[]  # TODO: [(args, kwargs), ...] fixtures,
)
