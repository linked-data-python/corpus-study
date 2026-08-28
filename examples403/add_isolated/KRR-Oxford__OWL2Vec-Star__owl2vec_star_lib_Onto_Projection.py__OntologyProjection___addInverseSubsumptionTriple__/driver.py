"""Validation driver for KRR-Oxford__OWL2Vec-Star__owl2vec_star_lib_Onto_Projection.py__OntologyProjection___addInverseSubsumptionTriple__.

Establishes semantic equivalence of original.py and translated.ldpy.
Filled in during translation review; see rdfeval.harness for helpers.
"""
from rdfeval.harness import run_pair

# entry=None executes both modules and compares every rdflib Graph found in
# the module globals (plus captured stdout).  For function regions, set
# entry="<function name>" and provide the fixture arguments.
VERDICT = run_pair(
    __file__,
    entry='__addInverseSubsumptionTriple__',
    calls=[]  # TODO: [(args, kwargs), ...] fixtures,
)
