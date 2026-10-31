"""Validation driver for BD2KOnFHIR__fhirtordf__tests_rdfsupport_tests_test_fhirgraphutils.py__FHIRGraphUtilsTestCase_test_value.

This region READS a graph, so the oracle is not isomorphism but the
equality of the values both versions produce from the same input graph
(design record corpus/405). `fixture.ttl` (this directory) is parsed by
the region ITSELF (`g.parse(os.path.join(self.base_dir, "fixture.ttl"),
format="turtle")`, see original.py's header for the load->parse and
filename-rename notes) rather than handed in as an argument, so `fixture=`
(which would parse the file and pass the graph to `entry`) does not apply
here -- `self.base_dir` supplies the directory to read it from instead.

`test_value` is a unittest.TestCase method that only ever asserts and
returns None, and needs `self` for both `.base_dir` (bound in the real
class's setUpClass) and the assert* methods -- `demo` (identical on both
sides, see original.py) turns a failed assertion into a comparable value
instead of letting it abort the driver, the same convention already used
by examples/trav_one_step/INM-6__alpaca__.../test_provenance_annotation_multiple_returns
in this study.

Added by the mutation audit of 2026-10-31.  The region reads a hard-coded
"fixture.ttl" under `self.base_dir`, so each extra call re-runs it with
base_dir pointing at a variants/<name>/ directory (same file name, other
content) -- a change of context line only, in the driver:
  * variants/two       -- two servicePeriods, each with two Period.end:
                          the two-solution case, where `.one()` raises.
  * variants/no_period -- no servicePeriod on the subject (zero solutions
                          for the first site; a neighbour has one).
  * variants/no_end    -- a period without Period.end (zero solutions for
                          the second site; a neighbour has one).
  * variants/repo      -- the repository's own tests/data/account-example.ttl,
                          verbatim.
In fixture.ttl itself the neighbour <Patient/example> now comes first, so a
subject widened to `[]` reads its period before the right one.  A failed
assertion comes back from demo as ("assertion-failed", msg), on both sides
alike; `.one()` or `next(iter(...))` raise a different exception instead.
"""
import unittest
from pathlib import Path

from rdfeval.harness import run_pair

HERE = Path(__file__).resolve().parent


class _Case(unittest.TestCase):
    """Stand-in for FHIRGraphUtilsTestCase: only .base_dir (bound by the
    real class's setUpClass) and the assert* methods (inherited from
    unittest.TestCase, unmodified) are needed by the extracted method."""
    base_dir = str(HERE)

    def runTest(self):
        pass


def call_default():
    # A fresh _Case per invocation; nothing here is mutated or shared.
    return ((_Case(),), {})


def _variant_call(name):
    def call():
        case = _Case()
        case.base_dir = str(HERE / "variants" / name)
        return ((case,), {})
    call.__name__ = "call_" + name
    return call


VARIANT_CALLS = [_variant_call(n) for n in ("two", "no_period", "no_end", "repo")]


VERDICT = run_pair(
    __file__,
    entry='demo',
    calls=[call_default] + VARIANT_CALLS,
)
