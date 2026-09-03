"""Validation driver for BD2KOnFHIR__fhirtordf__tests_rdfsupport_tests_test_fhirgraphutils.py__FHIRGraphUtilsTestCase_test_value.

This region READS a graph, so the oracle is not isomorphism but the
equality of the values both versions produce from the same input graph
(design record corpus/405). `fixture.ttl` (this directory) is parsed by
the region ITSELF (`g.parse(os.path.join(self.base_dir, "fixture.ttl"),
format="turtle")`, see original.py's header for the load->parse and
filename-rename notes) rather than handed in as an argument, so `fixture=`
(which would parse the file and pass the graph to `entry`) does not apply
here -- `self.base_dir` supplies the directory to read it from instead.

`test_value` is a unittest.TestCase method that only ever asserts and
returns None, and needs `self` for both `.base_dir` (bound in the real
class's setUpClass) and the assert* methods -- `demo` (identical on both
sides, see original.py) turns a failed assertion into a comparable value
instead of letting it abort the driver, the same convention already used
by examples/trav_one_step/INM-6__alpaca__.../test_provenance_annotation_multiple_returns
in this study.
"""
import unittest
from pathlib import Path

from rdfeval.harness import run_pair

HERE = Path(__file__).resolve().parent


class _Case(unittest.TestCase):
    """Stand-in for FHIRGraphUtilsTestCase: only .base_dir (bound by the
    real class's setUpClass) and the assert* methods (inherited from
    unittest.TestCase, unmodified) are needed by the extracted method."""
    base_dir = str(HERE)

    def runTest(self):
        pass


def call_default():
    # A fresh _Case per invocation; nothing here is mutated or shared.
    return ((_Case(),), {})


VERDICT = run_pair(
    __file__,
    entry='demo',
    calls=[call_default],
)
