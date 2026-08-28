"""Validation driver for linkml__linkml__tests_linkml_test_compliance_test_compliance.py__<module>.

The region is a constants module: it defines no function and builds no graph,
so both sides carry an identical `demo harness` section (see meta.json) that
uses EXAMPLE_NS and a few of the constants to build DEMO_GRAPH.  entry=None
therefore compares DEMO_GRAPH (isomorphism) plus the captured stdout.
"""
from rdfeval.harness import run_pair

VERDICT = run_pair(
    __file__,
    entry=None,
    calls=None,
)
