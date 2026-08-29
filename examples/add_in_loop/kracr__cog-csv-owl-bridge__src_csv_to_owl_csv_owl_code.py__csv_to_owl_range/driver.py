"""Validation driver for kracr__cog-csv-owl-bridge__src_csv_to_owl_csv_owl_code.py__csv_to_owl_range.

Establishes semantic equivalence of original.py and translated.ldpy.
Filled in during translation review; see rdfeval.harness for helpers.
"""
from rdfeval.harness import run_pair

# entry=None executes both modules and compares every rdflib Graph found in
# the module globals (plus captured stdout).  For function regions, set
# entry="<function name>" and provide the fixture arguments.
VERDICT = run_pair(
    __file__,
    entry='csv_to_owl_range',
    calls=[]  # TODO: [(args, kwargs), ...] fixtures,
)
