"""Validation driver for matthiasprobst__h5RDMtoolbox__tests_ld_test_ld.py__TestLinkedData_test_dump_dataset_data_using_serialize_0D_datasets.

Establishes semantic equivalence of original.py and translated.ldpy.
Filled in during translation review; see rdfeval.harness for helpers.
"""
from rdfeval.harness import run_pair

# entry=None executes both modules and compares every rdflib Graph found in
# the module globals (plus captured stdout).  For function regions, set
# entry="<function name>" and provide the fixture arguments.
VERDICT = run_pair(
    __file__,
    entry='test_dump_dataset_data_using_serialize_0D_datasets',
    calls=[]  # TODO: [(args, kwargs), ...] fixtures,
)
