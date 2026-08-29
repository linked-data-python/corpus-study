"""Validation driver for tetherless-world__materialsmine__tests_test_L155_S2_Roy_2005.py__IngestTestRunner_no_test_dielectric_real_permittivity.

The region only builds Python values -- a list of rdflib.Literal frequency
readings, a list of rdflib.Literal real-permittivity readings, and a dict of
three rdflib.Literal descriptions -- then hands them to
ingest_tester.test_dielectric_real_permittivity. It never returns anything of
its own (no `return` in the region) and never touches a graph. The real
ingest_tester queries a live triple store (see context_shim.py), so the
shim's stand-in just prints a term-by-term (value, datatype) view of what it
receives: the oracle is that printed view agreeing between original.py and
translated.ldpy, which is exactly the coercion this region performs.

`self` (materialsmine calls it `runner`) is never inspected by the region or
by the shim, so a bare None stands in for it.
"""
from rdfeval.harness import run_pair

VERDICT = run_pair(
    __file__,
    entry='no_test_dielectric_real_permittivity',
    calls=[((None,), {})],
)
