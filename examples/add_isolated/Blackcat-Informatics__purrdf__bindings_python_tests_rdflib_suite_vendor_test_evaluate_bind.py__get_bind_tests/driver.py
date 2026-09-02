"""Validation driver for Blackcat-Informatics__purrdf__bindings_python_tests_rdflib_suite_vendor_test_evaluate_bind.py__get_bind_tests.

get_bind_tests BUILDS a graph (the region's one triple_add is the
add_isolated site under test), so the right oracle is graph isomorphism
(design record corpus/403), not value equality -- but the graph is never
returned or assigned at module level: it is a variable local to the
generator, invisible from outside it.

run_pair's built-in entry=/calls= comparison would only see what
get_bind_tests() *returns*: a generator of 4-tuples ``(check, expr, var,
obj)`` where ``check`` is a function NESTED inside get_bind_tests, closing
over `g`. Two module executions produce two distinct function objects for
``check``, so comparing yielded tuples with ``==`` would report a
difference on every run regardless of translation -- a false FAIL, not a
signal about the region. Nor does re-running check(expr, var, obj) itself
prove much: its query is `?s ?p ?o . BIND(...)`, an unconstrained triple
pattern joined with a BIND whose value never depends on the matched triple
-- it only proves *some* triple exists, not that it is the RIGHT one.

So this driver reaches the graph directly: `check.__closure__` holds a cell
for the free variable `g` (confirmed via `check.__code__.co_freevars ==
('g',)`), i.e. the very Graph the region's g.add()/+{ } built. Extracting
that cell on both sides and comparing by isomorphism is precisely the
add_isolated oracle, undistorted by the incidental nested-function/BIND
scaffolding around it. The yielded (expr, var, obj) literals -- unaffected
by the "different function object" problem -- are compared too, as a cheap
extra check that the generator's own structure was not altered.

Following the precedent of driving both sides by hand when run_pair's
default comparison cannot see the state under test: add_isolated/
BBDFrancois.../driver.py and add_isolated/TheWorldAvatar/.../driver.py.
"""
from __future__ import annotations

import traceback
from pathlib import Path

from rdfeval.harness import _exec_ldpy, _exec_python, _emit, graphs_isomorphic

HERE = Path(__file__).resolve().parent

verdict = {"example": HERE.name, "equivalent": False,
           "method": "entry:get_bind_tests (hand-rolled: graph reached via "
                     "check.__closure__, compared by isomorphism)",
           "diffs": [], "error": None}


def _graph_from_check(check_fn):
    names = check_fn.__code__.co_freevars
    cells = check_fn.__closure__
    for name, cell in zip(names, cells):
        if name == "g":
            return cell.cell_contents
    raise RuntimeError(f"no 'g' free variable on {check_fn!r} "
                       f"(freevars={names!r})")


try:
    ns_o, out_o = _exec_python(HERE / "original.py")
    ns_t, out_t = _exec_ldpy(HERE / "translated.ldpy")
    fo = ns_o.get("get_bind_tests")
    ft = ns_t.get("get_bind_tests")
    if not callable(fo) or not callable(ft):
        raise RuntimeError("entry point not found in both modules")

    items_o = list(fo())
    items_t = list(ft())

    diffs: list[str] = []
    if len(items_o) != len(items_t):
        diffs.append(f"yielded {len(items_o)} items vs {len(items_t)}")
    else:
        for i, ((check_o, expr_o, var_o, obj_o),
                (check_t, expr_t, var_t, obj_t)) in enumerate(zip(items_o, items_t)):
            if (expr_o, var_o, obj_o) != (expr_t, var_t, obj_t):
                diffs.append(f"item[{i}]: (expr, var, obj) differ "
                             f"({(expr_o, var_o, obj_o)!r} vs "
                             f"{(expr_t, var_t, obj_t)!r})")

    if items_o and items_t:
        go = _graph_from_check(items_o[0][0])
        gt = _graph_from_check(items_t[0][0])
        if not graphs_isomorphic(go, gt):
            diffs.append(f"graph built by get_bind_tests not isomorphic "
                         f"({len(go)} vs {len(gt)} triples)")

    if out_o != out_t:
        diffs.append(f"stdout differs ({out_o[:200]!r} vs {out_t[:200]!r})")

    verdict["diffs"] = diffs
    verdict["equivalent"] = not diffs
except Exception:
    verdict["error"] = traceback.format_exc(limit=8)

_emit(verdict)
VERDICT = verdict
