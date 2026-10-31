"""Validation driver for RDFLib__timefuncs__tests_functions_test_finishes.py__test_finishes.

`test_finishes` is a pytest test: it loads its own fixture at a hardcoded
relative path (`tests_dir / "data" / "finishes.ttl"`, `tests_dir =
Path(__file__).parent`) -- see `data/finishes.ttl`, the real upstream fixture
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

Mutation audit of 2026-10-30.  The first call only says that the upstream
assertion holds on both sides.  The only ProperInterval in the upstream
data that finishes another one is `a08`, an `?a`: replacing
time:ProperInterval in `VALUES ?b_type` alone, doubling it there, or adding
DISTINCT all stayed green.  The other calls pass `demo(run=...)`, a seam
identical on both sides (same as the test_starts region), and `observe`
below:

  * records every call the SPARQL engine makes to tfun:finishes -- one per
    solution of the VALUES + type patterns, with its arguments and its
    verdict -- by wrapping the function registered by context_shim.py in
    rdflib's (global, shared) registry for the duration of the call only;
  * records the list the test hands to `sorted(...)` -- its `actual`, the
    query's answer with its multiplicity -- through a `sorted` placed in
    the test's module globals for the duration of the call only (the
    upstream assertion is a bare `assert`, so its failure carries no value);
  * optionally points the test's module-level `tests_dir` at a temporary
    directory holding another `data/finishes.ttl` (restored afterwards).
  The test's own outcome (passes, or which exception) is returned beside.

Calls:
  1. `demo()` -- unchanged: the upstream test passes on both sides.
  2. upstream data, observed: candidate rows, verdicts and `actual`.
  3. NEIGHBOURS: a ProperInterval pair linked by time:intervalFinishes (a
     solution only through the ProperInterval branch of `VALUES ?b_type`),
     a node typed both Interval and ProperInterval (two rows per partner,
     so `actual` holds a duplicate), a time:Instant and a
     time:DateTimeInterval linked by intervalFinishes (types absent from
     VALUES: must not be candidates).  The upstream assertion fails on both
     sides -- compared as an outcome, beside the rows.
  4. ZERO solutions: data with no interval at all.
"""
import builtins
import tempfile
from pathlib import Path

from rdflib import Namespace
from rdflib.plugins.sparql.operators import _CUSTOM_FUNCTIONS

from rdfeval.harness import run_pair

TFUN = Namespace("https://w3id.org/timefuncs/")

NEIGHBOURS = """\
PREFIX time: <http://www.w3.org/2006/time#>
PREFIX : <https://w3id.org/timefuncs/testdata/finishes/>
:p1 a time:ProperInterval . :q1 a time:ProperInterval .
:p1 time:intervalFinishes :q1 .
:p2 a time:Interval , time:ProperInterval .
:p2 time:intervalFinishes :q1 .
:i3 a time:Instant . :i3 time:intervalFinishes :q1 .
:r4 a time:DateTimeInterval . :r4 time:intervalFinishes :q1 .
"""
ZERO = """\
PREFIX time: <http://www.w3.org/2006/time#>
PREFIX : <https://w3id.org/timefuncs/testdata/finishes/>
:i1 a time:Instant . :i1 time:intervalFinishes :i2 .
"""


def observe(data=None):
    """A `run` for demo(): the test's tfun:finishes calls, its `actual`
    and its outcome."""
    def run(test):
        calls, sorted_args = [], []
        func, raw = _CUSTOM_FUNCTIONS[TFUN.finishes]

        def recorder(e, ctx):
            verdict = func(e, ctx)
            calls.append((str(e.expr[0]), str(e.expr[1]), verdict.toPython()))
            return verdict

        def recording_sorted(iterable, *args, **kwargs):
            result = builtins.sorted(iterable, *args, **kwargs)
            sorted_args.append(list(result))
            return result

        module = test.__globals__
        saved_dir = module["tests_dir"]
        tmp = tempfile.TemporaryDirectory() if data is not None else None
        if tmp is not None:
            (Path(tmp.name) / "data").mkdir()
            (Path(tmp.name) / "data" / "finishes.ttl").write_text(data)
            module["tests_dir"] = Path(tmp.name)
        _CUSTOM_FUNCTIONS[TFUN.finishes] = (recorder, raw)
        module["sorted"] = recording_sorted
        try:
            test()
            outcome = "passed"
        except Exception as exc:              # noqa: BLE001 - compared
            outcome = (type(exc).__name__, str(exc))
        finally:
            _CUSTOM_FUNCTIONS[TFUN.finishes] = (func, raw)
            del module["sorted"]
            module["tests_dir"] = saved_dir
            if tmp is not None:
                tmp.cleanup()
        return sorted(calls), sorted_args, outcome
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
