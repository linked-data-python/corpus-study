"""Validation driver for Mat-O-Lab__ckanext-csvtocsvw__ckanext_csvtocsvw_csvw_parser.py__CSVWtoRDF_add_table_data.

Establishes semantic equivalence of original.py and translated.ldpy.
Filled in during translation review; see rdfeval.harness for helpers.
"""
from rdfeval.harness import run_pair

# entry=None executes both modules and compares every rdflib Graph found in
# the module globals (plus captured stdout).  For function regions, set
# entry="<function name>" and provide the fixture arguments.
VERDICT = run_pair(
    __file__,
    entry='add_table_data',
    calls=[]  # TODO: [(args, kwargs), ...] fixtures,
)
