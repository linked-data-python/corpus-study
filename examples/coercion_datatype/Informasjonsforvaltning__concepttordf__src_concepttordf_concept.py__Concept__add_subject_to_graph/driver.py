"""Validation driver for Informasjonsforvaltning__concepttordf__src_concepttordf_concept.py__Concept__add_subject_to_graph.

Establishes semantic equivalence of original.py and translated.ldpy.
Filled in during translation review; see rdfeval.harness for helpers.
"""
from rdfeval.harness import run_pair

# entry=None executes both modules and compares every rdflib Graph found in
# the module globals (plus captured stdout).  For function regions, set
# entry="<function name>" and provide the fixture arguments.
VERDICT = run_pair(
    __file__,
    entry='_add_subject_to_graph',
    calls=[]  # TODO: [(args, kwargs), ...] fixtures,
)
