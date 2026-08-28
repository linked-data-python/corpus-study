"""Validation driver for RDFLib__pyLODE__pylode_profiles_supermodel_query___init__.py__Query_get_supermodel_iri.

Establishes semantic equivalence of original.py and translated.ldpy.
Filled in during translation review; see rdfeval.harness for helpers.
"""
from rdfeval.harness import run_pair

# entry=None executes both modules and compares every rdflib Graph found in
# the module globals (plus captured stdout).  For function regions, set
# entry="<function name>" and provide the fixture arguments.
VERDICT = run_pair(
    __file__,
    entry='get_supermodel_iri',
    calls=[]  # TODO: [(args, kwargs), ...] fixtures,
)
