"""Validation driver for LexMalta__recipes__recipe-importer_rdflib_plugins_sparql_results_csvresults.py__CSVResultParser_convertTerm.

Establishes semantic equivalence of original.py and translated.ldpy.
Filled in during translation review; see rdfeval.harness for helpers.
"""
from rdfeval.harness import run_pair

# entry=None executes both modules and compares every rdflib Graph found in
# the module globals (plus captured stdout).  For function regions, set
# entry="<function name>" and provide the fixture arguments.
VERDICT = run_pair(
    __file__,
    entry='convertTerm',
    calls=[]  # TODO: [(args, kwargs), ...] fixtures,
)
