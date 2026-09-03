"""Validation driver for RDFLib__timefuncs__tests_functions_test_starts.py__test_starts.

`test_starts` is a pytest test: it loads its own fixture at a hardcoded
relative path (`tests_dir / "data" / "starts.ttl"`, `tests_dir =
Path(__file__).parent`) -- see `data/starts.ttl`, the real upstream fixture
copied verbatim, which both `original.py` and `translated.ldpy` resolve
correctly under their own `__file__` with NO path-fixing code needed -- runs
a query, asserts the result against a hardcoded `expected`, and returns
nothing.  Calling it directly through `entry=`/`calls=` would therefore give
`run_pair` nothing to compare (no return value, no mutated argument, no
stdout: the "nothing observable" guard in rdfeval.harness), even though an
AssertionError on either side already fails the whole check -- which is the
region's own pass/fail criterion.  `demo`, identical on both files (see
meta.json), runs the test and returns a sentinel so run_pair has something
to compare.

`initNs={"time": TIME, "tfun": TFUN}` is the region's ONLY rdflib binding
kwarg here -- there is no `initBindings`, so per the batch warning about
initNs-only regions in this stratum, this region needs no interpolation:
only `@prefix time:` / `@prefix tfun:` in scope (see meta.json).
"""
from rdfeval.harness import run_pair

VERDICT = run_pair(
    __file__,
    entry="demo",
    calls=[((), {})],
)
