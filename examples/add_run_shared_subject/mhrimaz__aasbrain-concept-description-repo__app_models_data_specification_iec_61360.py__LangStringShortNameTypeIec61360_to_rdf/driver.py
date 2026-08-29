"""Validation driver for mhrimaz__aasbrain-concept-description-repo__app_models_data_specification_iec_61360.py__LangStringShortNameTypeIec61360_to_rdf.

Establishes semantic equivalence of original.py and translated.ldpy.
Filled in during translation review; see rdfeval.harness for helpers.
"""
from rdfeval.harness import run_pair

# entry=None executes both modules and compares every rdflib Graph found in
# the module globals (plus captured stdout).  For function regions, set
# entry="<function name>" and provide the fixture arguments.
VERDICT = run_pair(
    __file__,
    entry='to_rdf',
    calls=[]  # TODO: [(args, kwargs), ...] fixtures,
)
