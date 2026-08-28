"""Validation driver: the region is a pytest method whose only argument is self.

It builds a one-quad Dataset around a 33-character BNode name, runs
Nanopub._replace_blank_nodes over it and asserts the quad count.  The Dataset
is created inside the region, so the comparison rests on the region's own
assert (an assertion failure on either side surfaces as an error in the
verdict); `self` is unused, so a None stand-in is passed.
"""
from rdfeval.harness import run_pair

VERDICT = run_pair(__file__, entry="test_replace_blank_nodes_unnamed_bnode",
                   calls=[lambda: ((None,), {})])
