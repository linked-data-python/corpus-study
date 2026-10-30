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

Repair of 2026-10-30 (triage: weak-oracle).  The first call only says that
the upstream assertion holds on both sides; no ProperInterval pair of the
upstream data satisfies tfun:starts, so the `time:ProperInterval` half of
both VALUES went unobserved (a mutant replacing it stayed green).  The
other calls pass `demo(run=...)`, a seam identical on both sides, and
`observe` below:

  * records every call the SPARQL engine makes to tfun:starts -- one per
    solution of the VALUES + type patterns, with its arguments and its
    verdict -- by wrapping the function registered by context_shim.py in
    rdflib's (global, shared) registry for the duration of the call only.
    The sorted multiset of (a, b, verdict) is the candidate rows and, with
    the verdicts, the query's whole answer; the test's own outcome (passes,
    or which exception) is returned beside it;
  * optionally points the test's module-level `tests_dir` at a temporary
    directory holding another `data/starts.ttl` (restored afterwards), so
    the same test reads data the upstream file does not have.

Calls:
  1. `demo()` -- unchanged: the upstream test passes on both sides.
  2. upstream data, observed: the candidate rows include the ProperInterval
     ones (a09/b09, a10/b10) even though none of them starts another.
  3. NEIGHBOURS: a ProperInterval pair linked by time:intervalStarts (a
     solution only through the ProperInterval branch of both VALUES), a node
     typed both Interval and ProperInterval (two rows per partner: the
     multiset counts them), a time:Instant and a time:DateTimeInterval
     linked by intervalStarts (must not be candidates: a type absent from
     VALUES).  The upstream assertion fails on both sides -- compared as an
     outcome, beside the rows.
  4. ZERO solutions: data with no interval at all -- no row, the assertion
     fails on both sides.
"""
import tempfile
from pathlib import Path

from rdflib import Namespace
from rdflib.plugins.sparql.operators import _CUSTOM_FUNCTIONS

from rdfeval.harness import run_pair

TFUN = Namespace("https://w3id.org/timefuncs/")

NEIGHBOURS = """\
PREFIX time: <http://www.w3.org/2006/time#>
PREFIX : <https://w3id.org/timefuncs/testdata/starts/>
:p1 a time:ProperInterval . :q1 a time:ProperInterval .
:p1 time:intervalStarts :q1 .
:p2 a time:Interval , time:ProperInterval .
:p2 time:intervalStarts :q1 .
:i3 a time:Instant . :i3 time:intervalStarts :q1 .
:r4 a time:DateTimeInterval . :r4 time:intervalStarts :q1 .
"""
ZERO = """\
PREFIX time: <http://www.w3.org/2006/time#>
PREFIX : <https://w3id.org/timefuncs/testdata/starts/>
:i1 a time:Instant . :i1 time:intervalStarts :i2 .
"""


def observe(data=None):
    """A `run` for demo(): the test's tfun:starts calls and its outcome."""
    def run(test):
        calls = []
        func, raw = _CUSTOM_FUNCTIONS[TFUN.starts]

        def recorder(e, ctx):
            verdict = func(e, ctx)
            calls.append((str(e.expr[0]), str(e.expr[1]), verdict.toPython()))
            return verdict

        module = test.__globals__
        saved_dir = module["tests_dir"]
        tmp = tempfile.TemporaryDirectory() if data is not None else None
        if tmp is not None:
            (Path(tmp.name) / "data").mkdir()
            (Path(tmp.name) / "data" / "starts.ttl").write_text(data)
            module["tests_dir"] = Path(tmp.name)
        _CUSTOM_FUNCTIONS[TFUN.starts] = (recorder, raw)
        try:
            test()
            outcome = "passed"
        except Exception as exc:              # noqa: BLE001 - compared
            outcome = (type(exc).__name__, str(exc))
        finally:
            _CUSTOM_FUNCTIONS[TFUN.starts] = (func, raw)
            module["tests_dir"] = saved_dir
            if tmp is not None:
                tmp.cleanup()
        return sorted(calls), outcome
    return lambda: ((run,), {})


VERDICT = run_pair(
    __file__,
    entry="demo",
    calls=[
        ((), {}),               # the upstream test as such
        observe(),              # upstream data: every candidate row
        observe(NEIGHBOURS),    # ProperInterval solution, duplicates, types
        observe(ZERO),          # zero solution
    ],
)
