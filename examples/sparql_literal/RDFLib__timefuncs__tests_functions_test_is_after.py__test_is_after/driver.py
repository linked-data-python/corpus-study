"""Validation driver for RDFLib__timefuncs__tests_functions_test_is_after.py__test_is_after.

This region reads a graph (design record corpus/405), but `test_is_after`
takes no argument: it builds its own graph from a fixed relative path
(`tests_dir / "data" / "after.ttl"`, restored verbatim at `data/after.ttl` --
see meta.json), so run_pair's `fixture=` mechanism (which injects ONE parsed
graph as the entry point's sole argument) does not apply here.  The entry
point is `demo`, a seam identical on both files (see meta.json): `demo()`
is exactly the former call of `test_is_after()` and returns the sorted
`actual` list the test builds.

Repair of 2026-10-31 (mutation audit).  Every node of the upstream data
that is typed at all is a time:TemporalEntity, so widening either type
pattern (`?a a ?t`, `?a ?p time:TemporalEntity`, the same for ?b) stayed
green.  The other calls pass `demo(run=...)` and `observe` below:

  * records every call the SPARQL engine makes to tfun:isAfter -- one per
    solution of the two type patterns, with its arguments and its verdict
    (or the exception it raised) -- by wrapping the function registered by
    _context.py in rdflib's (global, shared) registry for the duration of
    the call only.  The sorted multiset of (a, b, verdict) is the candidate
    rows and, with the verdicts, the query's whole answer; the test's own
    outcome (what it returned, or which exception) is returned beside it;
  * optionally points the test's module-level `tests_dir` at a temporary
    directory holding another `data/after.ttl` (restored afterwards), so
    the same test reads data the upstream file does not have.

`_context` is imported once and cached in sys.modules, so both sides call
the same `is_after`; that is harmless here (the shim is identical for both
representations and stateless), and the recorder wraps whatever is
registered when each side runs.

Calls:
  1. `demo()` -- the upstream test: 22 expected pairs, returned.
  2. upstream data, observed: all 20 x 20 candidate rows and their verdicts.
  3. NEIGHBOURS: one solution (:a1 after :b1); a time:Instant and a node
     that only mentions time:TemporalEntity through rdfs:seeAlso, both
     `time:after :b1` (each shares two terms with a type pattern: they
     must not be candidates); :b1 typed twice (TemporalEntity and Instant:
     a widened ?b type pattern doubles its rows).  The upstream assertion
     fails on both sides -- compared as an outcome, beside the rows.
  4. ZERO solutions: two time:Instant nodes linked by time:after, no
     TemporalEntity at all -- no candidate row.
"""
import tempfile
from pathlib import Path

from rdflib import Namespace
from rdflib.plugins.sparql.operators import _CUSTOM_FUNCTIONS

from rdfeval.harness import run_pair

TFUN = Namespace("https://w3id.org/timefuncs/")

NEIGHBOURS = """\
PREFIX time: <http://www.w3.org/2006/time#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX : <https://w3id.org/timefuncs/testdata/after/>
:i1 a time:Instant ; time:after :b1 .
:s1 rdfs:seeAlso time:TemporalEntity ; time:after :b1 .
:a1 a time:TemporalEntity ; time:after :b1 .
:b1 a time:TemporalEntity , time:Instant .
"""
ZERO = """\
PREFIX time: <http://www.w3.org/2006/time#>
PREFIX : <https://w3id.org/timefuncs/testdata/after/>
:i1 a time:Instant ; time:after :i2 .
:i2 a time:Instant .
"""


def observe(data=None):
    """A `run` for demo(): the test's tfun:isAfter calls and its outcome."""
    def run(test):
        calls = []
        func, raw = _CUSTOM_FUNCTIONS[TFUN.isAfter]

        def recorder(e, ctx):
            row = (str(e.expr[0]), str(e.expr[1]))
            try:
                verdict = func(e, ctx)
            except Exception as exc:          # noqa: BLE001 - recorded
                calls.append(row + (type(exc).__name__,))
                raise
            calls.append(row + (str(verdict.toPython()),))
            return verdict

        module = test.__globals__
        saved_dir = module["tests_dir"]
        tmp = tempfile.TemporaryDirectory() if data is not None else None
        if tmp is not None:
            (Path(tmp.name) / "data").mkdir()
            (Path(tmp.name) / "data" / "after.ttl").write_text(data)
            module["tests_dir"] = Path(tmp.name)
        _CUSTOM_FUNCTIONS[TFUN.isAfter] = (recorder, raw)
        try:
            outcome = ("returned", test())
        except Exception as exc:              # noqa: BLE001 - compared
            outcome = (type(exc).__name__, str(exc))
        finally:
            _CUSTOM_FUNCTIONS[TFUN.isAfter] = (func, raw)
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
        observe(NEIGHBOURS),    # Instant / seeAlso neighbours, double type
        observe(ZERO),          # zero solution
    ],
)
