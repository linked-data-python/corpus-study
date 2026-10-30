"""Validation driver for usc-isi-i2__etk__etk_unit_tests_test_kg_shacl.py__TestSHACLOntoConverter_test_cnode.

test_cnode is a unittest method: it takes no fixture, builds two IRIs
(`c1`, `c2`) and a converter, and asserts.  What it decides is therefore:

  * the TERMS it hands to the converter -- `converter.cnode(c1)`,
    `cnode('http://…')`, `cnode(c2)`, and `SHACLOntoConverter({str(c1): …})`.
    `cnode` does `str(class_)`, so an assertion log alone cannot tell
    `<http://example.org/Person>` from the bare string: the triage showed
    that mutant staying green.  The driver records, per call, the TYPE and
    the string of the argument, and the node it gets back;
  * the sequence of assertions and their outcomes.  The asserts carry no
    message, so a failing one is identified by its position in the log, not
    by the text of the AssertionError (which holds object addresses).

The seam: `demo(case=None)` (identical on both sides) runs test_cnode with
the TestCase it is given.  Two calls:

  1. `demo()` -- the original call, kept: a plain unittest.TestCase;
  2. `demo(recorder)` -- a TestCase whose top-level assert* calls are logged
     as (method, normalised arguments, passed|failed).

Normalisation, per side: an etk BNode is named by the order in which its
(random uuid) value first appears, so `cnode1 == cnode2` shows as the same
name; an etk URI keeps its value; an rdflib term or a str keeps its type and
string; a class is its name.

Shared state, isolated per side: the converter class comes from the shim
module, cached in `sys.modules`.  The driver wraps its `__init__` and `cnode`
to record what the region passes; to keep the two sides from patching ONE
class, it drops `etk_context` from `sys.modules` before each side and checks
that the two classes are distinct.

Also compared: the outcome of each call (value, or exception type -- and,
for an AssertionError, which assertion failed), warnings, stdout, stderr.
"""
import contextlib
import functools
import io
import sys
import traceback
import unittest
import warnings
from pathlib import Path

from rdfeval.harness import _compare_value, _emit, _exec_ldpy, _exec_python

HERE = Path(__file__).resolve().parent
SHIM = "etk_context"


class Normaliser:
    """Comparable, side-independent descriptions of the values seen."""

    def __init__(self, shim):
        self.shim = shim
        self.bnodes: dict = {}

    def __call__(self, v):
        s = self.shim
        if isinstance(v, type):
            return ("class", v.__name__)
        if isinstance(v, s.BNode):
            return ("etk.BNode", self.bnodes.setdefault(v.value, f"b{len(self.bnodes)}"))
        if isinstance(v, s.Node):
            return (f"etk.{type(v).__name__}", v.value)
        if isinstance(v, dict):
            return ("dict", sorted((self(k), self(x)) for k, x in v.items()))
        if isinstance(v, (list, tuple)):
            return (type(v).__name__, [self(x) for x in v])
        if v is None or isinstance(v, (bool, int, float)):
            return v
        return (type(v).__name__, str(v))


def instrument(ns, log, norm):
    """Wrap this side's converter to record what the region passes it."""
    cls = ns["SHACLOntoConverter"]
    init, cnode = cls.__init__, cls.cnode

    @functools.wraps(init)
    def logged_init(self, *args, **kwargs):
        log.append(("SHACLOntoConverter", norm(args), norm(kwargs)))
        return init(self, *args, **kwargs)

    @functools.wraps(cnode)
    def logged_cnode(self, class_):
        arg = norm(class_)
        result = cnode(self, class_)
        log.append(("cnode", arg, norm(result)))
        return result

    cls.__init__, cls.cnode = logged_init, logged_cnode


def recorder_for(log, norm):
    class Recorder(unittest.TestCase):
        """A TestCase logging every top-level assert* call and its outcome."""
        _depth = 0

        def __getattribute__(self, name):
            attr = super().__getattribute__(name)
            if not name.startswith("assert") or not callable(attr):
                return attr

            def logged(*args, **kwargs):
                if Recorder._depth:
                    return attr(*args, **kwargs)
                entry = [name, norm(args), norm(kwargs), "passed"]
                log.append(entry)
                Recorder._depth += 1
                try:
                    return attr(*args, **kwargs)
                except AssertionError:
                    entry[3] = "failed"
                    raise
                finally:
                    Recorder._depth -= 1
            return logged

        def runTest(self):  # a TestCase needs one method to be instantiated
            pass

    return Recorder()


def observe(fn, args, log):
    out, err = io.StringIO(), io.StringIO()
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                outcome = ("returns", fn(*args))
            except AssertionError:
                # no message in the region's asserts: which one failed is
                # the observation (the text holds object addresses)
                outcome = ("raises", "AssertionError", f"after log entry {len(log) - 1}")
            except Exception as e:  # noqa: BLE001 -- the exception IS the observation
                outcome = ("raises", type(e).__name__, str(e))
    return {"outcome": outcome,
            "warnings": [(w.category.__name__, str(w.message)) for w in caught],
            "stdout": out.getvalue(), "stderr": err.getvalue(), "log": list(log)}


def run_side(execute, path, name):
    sys.modules.pop(SHIM, None)
    ns, out = execute(path, name)
    shim = sys.modules.pop(SHIM)
    return ns, out, shim


def side(ns, shim):
    """Both calls on one side: plain demo(), then demo(recorder)."""
    log: list = []
    norm = Normaliser(shim)
    instrument(ns, log, norm)
    results = [observe(ns["demo"], (), log)]
    log.clear()
    results.append(observe(ns["demo"], (recorder_for(log, norm),), log))
    return results


def main() -> dict:
    verdict: dict = {"example": HERE.name, "equivalent": False,
                     "method": "custom:assert-log+arguments, shim isolated per side",
                     "diffs": [], "error": None}
    try:
        ns_o, out_o, shim_o = run_side(_exec_python, HERE / "original.py", "__original__")
        ns_t, out_t, shim_t = run_side(_exec_ldpy, HERE / "translated.ldpy", "__translated__")
        diffs: list[str] = []
        if ns_o["SHACLOntoConverter"] is ns_t["SHACLOntoConverter"]:
            diffs.append("isolation broken: both sides share one converter class")
        res_o, res_t = side(ns_o, shim_o), side(ns_t, shim_t)
    except Exception:
        verdict["error"] = traceback.format_exc(limit=8)
        _emit(verdict)
        return verdict

    for i, (ro, rt) in enumerate(zip(res_o, res_t)):
        for key in ("outcome", "warnings", "stdout", "stderr", "log"):
            _compare_value(ro[key], rt[key], f"call[{i}].{key}", diffs)
    # the recorder must really have seen the region's assertions and calls
    asserts = [e for e in res_o[1]["log"] if isinstance(e, list)]
    if len(asserts) != 6 or res_o[1]["outcome"] != ("returns", "ok"):
        diffs.append(f"original: expected 6 passing asserts, saw {len(asserts)} "
                     f"and {res_o[1]['outcome']}")
    if out_o != out_t:
        diffs.append("stdout differs at module level")
    verdict["calls"] = 2
    verdict["log_entries"] = len(res_o[1]["log"])
    verdict["diffs"] = diffs
    verdict["equivalent"] = not diffs
    _emit(verdict)
    return verdict


VERDICT = main()
