"""Validation driver: the region is a pytest function taking no arguments.

It materialises the RMLTC0007c mapping with morph-kgc and asserts the result
is isomorphic to the expected output.nq; that assert is the check and it runs
on both sides.  The mapping/CSV/expected-output files live in this directory
(see meta.json), and the region resolves them relative to __file__.
"""
from rdfeval.harness import run_pair

VERDICT = run_pair(__file__, entry="test_RMLTC0007c", calls=[lambda: ((), {})])
