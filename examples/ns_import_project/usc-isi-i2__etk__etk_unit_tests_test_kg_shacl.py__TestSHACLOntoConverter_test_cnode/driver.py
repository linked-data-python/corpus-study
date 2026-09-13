"""Validation driver for usc-isi-i2__etk__etk_unit_tests_test_kg_shacl.py__TestSHACLOntoConverter_test_cnode.

test_cnode is a unittest method: it takes no fixture, only asserts on
values it builds itself and raises on the first failing assertion. The
`demo()` harness (identical on both sides, appended after the region, see
meta.json) supplies a plain `unittest.TestCase()` for `self` and returns a
sentinel string -- if either side's assertions fail, `demo()` raises and
`run_pair` reports the error; if both succeed silently, the sentinel is
what confirms it (an entry point observed only through "did not raise"
would otherwise be a hollow green).
"""
from rdfeval.harness import run_pair

VERDICT = run_pair(
    __file__,
    entry='demo',
    calls=[((), {})],
)
