"""Validation driver for DataDrivenCPS__acquirium__tests_src_graph_generator.py__build_test_graph_stream.

build_test_graph_stream takes no arguments and returns the graph it built:
a plain isomorphism comparison of two no-argument calls.
"""
from rdfeval.harness import run_pair

VERDICT = run_pair(
    __file__,
    entry='build_test_graph_stream',
    calls=[((), {})],
)
