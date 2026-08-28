"""Validation driver: the region is a pytest test taking no argument.

It parses the expected output.nq, materialises the same data with morph-kgc
from mapping.ttl and an in-memory dictionary, and asserts the two graphs are
isomorphic -- so calling it on both sides is the check.  mapping.ttl and
output.nq are copied next to the module (see meta.json); the region locates
them through os.path.realpath(__file__), which the harness sets to
original.py / translated.ldpy respectively.
"""
from rdfeval.harness import run_pair

VERDICT = run_pair(__file__, entry="test_RMLTC0007c", calls=[lambda: ((), {})])
