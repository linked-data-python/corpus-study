"""Validation driver for BBDFrancois__Web_Data_Project_DIA6_Royal_Family__src_m2_kb_construction.py__generate_dynamic_ontology.

Establishes semantic equivalence of original.py and translated.ldpy.
Filled in during translation review; see rdfeval.harness for helpers.
"""
from rdfeval.harness import run_pair

# entry=None executes both modules and compares every rdflib Graph found in
# the module globals (plus captured stdout).  For function regions, set
# entry="<function name>" and provide the fixture arguments.
VERDICT = run_pair(
    __file__,
    entry='generate_dynamic_ontology',
    calls=[]  # TODO: [(args, kwargs), ...] fixtures,
)
