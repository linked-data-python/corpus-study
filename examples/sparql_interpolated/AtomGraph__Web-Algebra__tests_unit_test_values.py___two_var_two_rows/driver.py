"""Validation driver for AtomGraph__Web-Algebra__tests_unit_test_values.py___two_var_two_rows.

The region builds its own two-triple graph (no external input) and returns
the rdflib ``Result`` of a SELECT over it, so there is no ``fixture.ttl`` to
inject: `_two_var_two_rows()` takes no argument.

``run_pair`` alone cannot be used here.  It materialises any iterable before
comparing, so a lazy prepared query (what ``return s{ ... }`` gives without
``(g).execute()``) and a real ``rdflib.query.Result`` look the same to it.
The repository does not accept the lazy one: ``Values.execute`` raises
``TypeError`` unless ``isinstance(data, Result)`` (web_algebra/operations/
sparql/values.py:67), then reads ``data.vars`` and ``data.bindings``, and
tests/unit/test_values.py:76 and :93 feed ``_two_var_two_rows()`` straight
into it.  So this driver calls each side's function and compares what that
caller relies on, for the two sides:

  * the type: ``isinstance(result, Result)`` and ``result.type == "SELECT"``;
  * ``result.vars`` (the projected columns, in order, ``[?s, ?o]``);
  * ``result.bindings`` (a list of dicts, so two rows with their terms:
    ``?s`` an IRI built from the ``str`` constants through ``URIRef``, ``?o``
    a plain literal), compared in order because the query says
    ``ORDER BY ?s``;
  * iterating the result (the rows as tuples), also ordered.

The function is called twice per side, to check that each call builds its own
graph and gives the same Result again.
"""
import json
import sys
from pathlib import Path

from rdflib.query import Result

from rdfeval import harness

ex_dir = Path(__file__).resolve().parent
verdict: dict = {"example": ex_dir.name, "equivalent": False,
                 "method": "entry:_two_var_two_rows (returned type, vars, bindings, rows)",
                 "ordered": True, "diffs": [], "error": None}


def observe(result):
    """What Values.execute relies on, as comparable data."""
    is_result = isinstance(result, Result)
    seen = {"is_rdflib_Result": is_result}
    if is_result:
        seen["result_type"] = result.type
        seen["vars"] = [str(v) for v in result.vars]
        seen["bindings"] = [{str(k): v for k, v in b.items()} for b in result.bindings]
        seen["rows"] = [tuple(row) for row in result]
    return seen


try:
    ns_o, _ = harness._exec_python(ex_dir / "original.py")
    ns_t, _ = harness._exec_ldpy(ex_dir / "translated.ldpy")
    diffs = []
    for call in range(2):
        obs_o = observe(ns_o["_two_var_two_rows"]())
        obs_t = observe(ns_t["_two_var_two_rows"]())
        if not obs_o["is_rdflib_Result"]:
            diffs.append(f"call[{call}]: original did not return an rdflib Result")
        for key in sorted(set(obs_o) | set(obs_t)):
            if obs_o.get(key) != obs_t.get(key):
                diffs.append(f"call[{call}].{key}: {obs_o.get(key)!r} vs {obs_t.get(key)!r}")
    verdict["diffs"] = diffs
    verdict["equivalent"] = not diffs
except Exception:
    import traceback
    verdict["error"] = traceback.format_exc(limit=8)

harness._emit(verdict)
VERDICT = verdict
