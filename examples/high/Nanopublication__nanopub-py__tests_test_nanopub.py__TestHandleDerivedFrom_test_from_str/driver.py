"""Validation driver: the region is a pytest method whose only argument is self.

It calls Nanopub._handle_derived_from with a plain string, then reads the
provenance graph back looking for the URIRef the translation turned into an
island: if the island denoted anything else, `found` would be empty and the
region's own assert would fail on that side, which the harness reports as an
execution error.  `self` is unused by the region, so a None stand-in is passed.
"""
from rdfeval.harness import run_pair

VERDICT = run_pair(__file__, entry="test_from_str", calls=[lambda: ((None,), {})])
