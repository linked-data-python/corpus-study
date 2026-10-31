"""Validation driver for RDFLib__timefuncs__tests_test_is_before_standalone.py__test_is_before_rdflib.

Establishes semantic equivalence of original.py and translated.ldpy.

The region is a test with no parameters: what it decides is WHICH terms it
passes to ``is_before_rdflib`` (30 ``BEFORE.xNN`` -> ``before:xNN``), and
in which order.  The ``run_pair`` call alone only sees the final
``return True``: it catches a wrong term in a POSITIVE assertion (the
assertion fails) but not in a NEGATIVE one, nor a dropped assertion --
``not is_before(g, a01, b03)`` is as true as ``not is_before(g, a01, b02)``.

So, on top of the ``run_pair`` call (kept as is), the driver runs each side
once more with ``is_before_rdflib`` replaced IN THAT SIDE'S MODULE GLOBALS
by a recorder that calls the real shim function (the repository's own
code, unchanged) and logs ``(a, b, result)``.  The recorder is the same
function on both sides, and each side gets its own log.  Compared:

  * the call log -- every term passed, in order, and every answer;
  * the outcome of the call (value, or exception type and message);
  * the module graph ``g`` afterwards (isomorphism): ``is_before_rdflib``
    writes ``time:after`` triples into the graph it is given, so a term
    that changes the inferred triples changes ``g`` too.

The extra diffs are merged into the single verdict ``run_pair`` emits.
"""
from rdfeval import harness
from rdfeval.harness import run_pair


def _recorded_runs():
    here = harness.Path(__file__).resolve().parent
    sides = []
    for exec_side, name in ((harness._exec_python, "original.py"),
                            (harness._exec_ldpy, "translated.ldpy")):
        ns, _ = exec_side(here / name)
        real = ns["is_before_rdflib"]
        log = []

        def recorder(g, a, b, _real=real, _log=log):
            result = _real(g, a, b)
            _log.append((a, b, result))
            return result

        ns["is_before_rdflib"] = recorder
        outcome = harness._outcome(ns["test_is_before_rdflib"], (), {})
        sides.append((outcome, log, ns["g"]))
    (oo, lo, go), (ot, lt, gt) = sides
    diffs = []
    if oo != ot:
        diffs.append(f"recorded run: outcome differs ({oo!r} vs {ot!r})")
    if lo != lt:
        first = next((i for i, (x, y) in enumerate(zip(lo, lt)) if x != y),
                     min(len(lo), len(lt)))
        diffs.append(f"recorded run: is_before_rdflib calls differ "
                     f"({len(lo)} vs {len(lt)} calls, first difference at "
                     f"call {first}: {lo[first:first + 1]} vs {lt[first:first + 1]})")
    harness._compare_value(go, gt, "recorded run: module graph g", diffs)
    return diffs


_EXTRA = _recorded_runs()
_emit = harness._emit


def _emit_with_recorder(verdict):
    verdict["diffs"] = list(verdict.get("diffs") or []) + _EXTRA
    verdict["equivalent"] = bool(verdict.get("equivalent")) and not _EXTRA
    _emit(verdict)


harness._emit = _emit_with_recorder

VERDICT = run_pair(
    __file__,
    entry='test_is_before_rdflib',
    calls=[((), {})],
)
