"""Validation driver for MaxBerktoldRWTH__BRICKbuilder__src_ontologies_namespaces___init__.py__<module>_9.

The region is one import line in a package ``__init__``:
``from src.ontologies.namespaces.qudt import QUDT, QUDTU, QUDTQK``.  It runs
no graph operation (rdf_ops=0).  What it decides is the set of names it
binds, and what the rest of the repository module does with them:

  * ``__all__`` (lines 30-32) re-exports QUDT, QUDTQK, QUDTU to the
    package's importers;
  * ``bindings`` (lines 56-58) uses the three classes as dict KEYS, and
    ``bind_namespaces`` (lines 139-145) binds them on graphs under their
    prefixes;
  * ``find_abbreviation`` (lines 88-98) compares IRIs against ``str(ns)``;
  * line 182 reads ``QUDT.degreeCelsius``, a term the class does not
    declare, so rdflib's DefinedNamespace emits a UserWarning.

This custom driver (``run_pair`` neither records warnings nor reports
``names_only_original`` outside module-state mode) observes all of it:

  1. ``names``: for each of QUDT, QUDTU, QUDTQK, whether the module binds it,
     and whether it is the shim's own object (same identity, same IRI).
     A prefix-only import (``from … import qudt:, …``, the first
     translation) binds none of them: the triage reproduced the NameError
     that ``bindings = {QUDT: …}`` raises then.
  2. ``names_only_original``: every public name the original module defines
     and the translation does not.  It must be empty -- the region binds
     names and nothing else, so a missing name is a missing effect.
  3. ``demo(case)``, the seam appended after the region (identical on both
     sides; only case "terms" is written in prefix notation on the
     translated side): its value or its exception (type and message), the
     warnings it emits (category and message), and what it prints to
     stdout and stderr.  The calls:
       - ``demo()``              (the original call, kept): one declared term
                                 of each namespace -- each prefix decides one
                                 component, so a swapped prefix shows;
       - ``demo("bindings")``    the key objects and the graph bindings;
       - ``demo("abbreviation")``which short name each of five IRIs gets
                                 (one per namespace, one outside, ``""``);
       - ``demo("main")``        ``QUDT.degreeCelsius`` and its warning;
       - ``demo("nope")``        the seam's own ValueError, so that the
                                 exception path is compared too.

Shared state, isolated per side: rdflib's ``DefinedNamespaceMeta.__getitem__``
is an ``lru_cache`` keyed on the class, so it warns about an undeclared
term only the FIRST time.  With the shim cached in ``sys.modules`` and its
classes shared, the second side read ``QUDT.degreeCelsius`` from the cache
and emitted no warning -- a false difference (or, the other way round, a
hidden one).  The driver therefore drops ``qudt_ns_context`` from
``sys.modules`` before executing each side, so each side imports its own
classes, and identity is checked against that side's own shim module.
"""
import contextlib
import io
import sys
import traceback
import warnings
from pathlib import Path

from rdfeval.harness import Raised, _compare_value, _emit, _exec_ldpy, _exec_python

SHIM = "qudt_ns_context"
NAMES = ("QUDT", "QUDTU", "QUDTQK")
CALLS = [((), {}), (("bindings",), {}), (("abbreviation",), {}),
         (("main",), {}), (("nope",), {})]


def observe(fn, args, kwargs):
    """Value or exception, warnings, stdout and stderr of one call."""
    out, err = io.StringIO(), io.StringIO()
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                result = fn(*args, **kwargs)
            except Exception as e:  # noqa: BLE001 -- the exception IS the observation
                result = Raised(e)
    return {"result": result,
            "warnings": [(w.category.__name__, str(w.message)) for w in caught],
            "stdout": out.getvalue(), "stderr": err.getvalue()}


def names(ns, shim):
    """What the region binds: presence, identity with the shim, IRI."""
    seen = {}
    for n in NAMES:
        if n not in ns:
            seen[n] = ("absent",)
        else:
            seen[n] = ("bound", ns[n] is getattr(shim, n, None), str(ns[n]))
    return seen


def public(ns):
    return {k for k in ns if not k.startswith("_")}


def main() -> dict:
    ex_dir = Path(__file__).resolve().parent
    verdict: dict = {"example": ex_dir.name, "equivalent": False,
                     "method": "custom:names+demo", "diffs": [], "error": None}
    try:
        sys.modules.pop(SHIM, None)
        ns_o, out_o = _exec_python(ex_dir / "original.py")
        shim_o = sys.modules.pop(SHIM)
        ns_t, out_t = _exec_ldpy(ex_dir / "translated.ldpy")
        shim_t = sys.modules[SHIM]
    except Exception:
        verdict["error"] = traceback.format_exc(limit=8)
        _emit(verdict)
        return verdict

    diffs: list[str] = []
    if shim_o is shim_t:
        diffs.append("the shim was not re-imported per side")
    _compare_value(names(ns_o, shim_o), names(ns_t, shim_t), "names bound", diffs)
    if any(v == ("absent",) for v in names(ns_o, shim_o).values()):
        diffs.append("the original does not bind every region name")
    only_o = sorted(public(ns_o) - public(ns_t))
    verdict["names_only_original"] = only_o
    if only_o:
        diffs.append(f"names only in the original: {only_o}")

    fo, ft = ns_o.get("demo"), ns_t.get("demo")
    if not callable(fo) or not callable(ft):
        verdict["error"] = "demo not found in both modules"
        _emit(verdict)
        return verdict
    raised = 0
    for i, (args, kwargs) in enumerate(CALLS):
        ro, rt = observe(fo, args, kwargs), observe(ft, args, kwargs)
        if isinstance(ro["result"], Raised) or isinstance(rt["result"], Raised):
            raised += isinstance(ro["result"], Raised)
            if ro["result"] != rt["result"]:
                diffs.append(f"call[{i}] {args}: outcome differs "
                             f"({ro['result']!r} vs {rt['result']!r})")
        else:
            _compare_value(ro["result"], rt["result"], f"call[{i}] {args}.result", diffs)
        for key in ("warnings", "stdout", "stderr"):
            if ro[key] != rt[key]:
                diffs.append(f"call[{i}] {args}: {key} differs ({ro[key]!r} vs {rt[key]!r})")
        if args == ("main",) and not ro["warnings"]:
            diffs.append("demo('main') emitted no warning: the case lost its point")
    if raised != 1:
        diffs.append(f"expected exactly one raising call on the original, got {raised}")
    if out_o != out_t:
        diffs.append("stdout differs at module level")

    verdict["calls"] = len(CALLS)
    verdict["diffs"] = diffs
    verdict["equivalent"] = not diffs
    _emit(verdict)
    return verdict


VERDICT = main()
