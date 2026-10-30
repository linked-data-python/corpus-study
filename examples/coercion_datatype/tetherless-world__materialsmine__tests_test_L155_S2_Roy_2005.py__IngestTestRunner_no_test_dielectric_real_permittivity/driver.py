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

Repair of 2026-10-30: the shim's view, (str, datatype), does not see a
language tag, nor the Python type of a term or of its containers -- a
`Literal("Frequency (Hz)", lang="en")` in place of the plain literal stayed
green.  The driver therefore wraps the shim's stand-in (the same module
object for both sides, so the wrapper is identical on each): after the
shim's own print, it prints the `repr()` of everything the region hands
over -- runner, both lists, the descriptions dict.  A term's repr carries its
class, lexical form, datatype and language, and the upstream comparison
(ingest_tester.py:588-594, `assertCountEqual` against store results) is term
equality, which repr equality implies.
"""
import context_shim
from rdfeval.harness import run_pair

_shim_view = context_shim.ingest_tester.test_dielectric_real_permittivity


def _recording(runner, frequency, real_permittivity, descriptions):
    _shim_view(runner, frequency, real_permittivity, descriptions)
    print("received:", repr(runner), repr(frequency), repr(real_permittivity),
          repr(descriptions))


context_shim.ingest_tester.test_dielectric_real_permittivity = _recording

VERDICT = run_pair(
    __file__,
    entry='no_test_dielectric_real_permittivity',
    calls=[((None,), {})],
)
