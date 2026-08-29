"""Validation driver for tgbugs__pyontutils__nifstd_nifstd_tools_parcellation_berman.py__BermanLabels__triples.

Establishes semantic equivalence of original.py and translated.ldpy.
Filled in during translation review; see rdfeval.harness for helpers.
"""
from rdfeval.harness import run_pair

# entry=None executes both modules and compares every rdflib Graph found in
# the module globals (plus captured stdout).  For function regions, set
# entry="<function name>" and provide the fixture arguments.
VERDICT = run_pair(
    __file__,
    entry='_triples',
    calls=[]  # TODO: [(args, kwargs), ...] fixtures,
)
