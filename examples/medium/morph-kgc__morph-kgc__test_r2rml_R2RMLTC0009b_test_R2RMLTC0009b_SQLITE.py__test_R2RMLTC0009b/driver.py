"""Validation driver: the region is a pytest test with no return value.

It materialises the R2RML mapping over the SQLite fixture and asserts the
result is isomorphic to output.nq; running it on both sides (fixtures copied
next to the sources, so os.path.dirname(__file__) resolves) shows that both
representations execute the same materialisation and pass the same assertion.
"""
from rdfeval.harness import run_pair

VERDICT = run_pair(
    __file__,
    entry='test_R2RMLTC0009b',
    calls=[lambda: ((), {})],
)
