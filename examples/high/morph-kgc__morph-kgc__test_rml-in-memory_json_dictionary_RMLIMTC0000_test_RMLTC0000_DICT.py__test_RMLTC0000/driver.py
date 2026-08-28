"""Validation driver: the region is a pytest test taking no argument.

mapping.ttl and output.nq (both tiny, Apache-2.0) were copied next to the
example so that os.path.dirname(os.path.realpath(__file__)) resolves for both
representations, which live in the same directory.  The test materialises a
python dictionary through morph-kgc and asserts isomorphism with the expected
output; calling it once on each side compares the assertion outcome.
"""
from rdfeval.harness import run_pair

VERDICT = run_pair(__file__, entry="test_RMLTC0000",
                   calls=[lambda: ((), {})])
