"""Validation driver for test_js_rules (pySHACL).

The region is a pytest test whose RDF content is two Turtle documents; the
ldpy side builds them as g{...} islands.  Both files end with the same small
demo harness that runs the test and exposes the two graphs handed to
validate(), so module-state comparison sees them and checks isomorphism.
"""
from rdfeval.harness import run_pair

VERDICT = run_pair(__file__)
