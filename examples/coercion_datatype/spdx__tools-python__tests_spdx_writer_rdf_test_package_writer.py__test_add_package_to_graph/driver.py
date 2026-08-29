"""Validation driver for spdx__tools-python__tests_spdx_writer_rdf_test_package_writer.py__test_add_package_to_graph.

Establishes semantic equivalence of original.py and translated.ldpy.
Filled in during translation review; see rdfeval.harness for helpers.
"""
from rdfeval.harness import run_pair

# entry=None executes both modules and compares every rdflib Graph found in
# the module globals (plus captured stdout).  For function regions, set
# entry="<function name>" and provide the fixture arguments.
VERDICT = run_pair(
    __file__,
    entry='test_add_package_to_graph',
    calls=[]  # TODO: [(args, kwargs), ...] fixtures,
)
