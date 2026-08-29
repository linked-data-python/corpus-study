"""Validation driver for
edmondchuc__rdflib-orm__tests_fields_test_irifield.py__<module>_1.

Not the generic ``run_pair(entry=None)`` shape: the region is a whole pytest
file, five ``test_*`` functions, none called at module import time (pytest
discovers and calls them; a plain ``exec`` of the file only *defines* them).
So module-state comparison would see zero graphs and empty stdout on both
sides -- "nothing observable to compare" -- regardless of whether the
translation is right.  What actually verifies this region is what the tests
already assert internally (``g.value(...) == URIRef('123')``, `pytest.raises`
around the expected exception): call each ``test_*`` in file order on each
side and record whether it completed or raised, and what.  A translation
mistake in ``rdf:``/``owl:``/``base:`` surfaces as an AssertionError on the
translated side where the original side says "ok" -- which the outcome
comparison below catches directly.

Two upstream fragility bugs are part of what must be reproduced identically,
not fixed: `Database.databases` is a *class* attribute of the shim's
`Database`, shared for the whole process, and the first two tests
(`test_required_field_raises`, `test_irifield_create`) never call
`Database.set_db()` themselves -- they only pass in the real suite because
some earlier test file has already set the 'default' entry.  Run standalone
(confirmed with ``pytest tests/fields/test_irifield.py`` against the
checked-out repo, corpus/repos/edmondchuc__rdflib-orm), both of them raise
``AttributeError: 'NoneType' object has no attribute 'base_uri'`` instead of
the ``FieldError``/success the test bodies read as if they expected.  Both
representations reuse the exact same shim classes (``orm_context`` is
imported once, cached in ``sys.modules``, by both `_exec_python` and
`_exec_ldpy`), so `Database.databases` is literally the same dict object on
both sides -- it is reset before each side's run so neither side's five
calls leak into the other's.
"""

import contextlib
import io
import sys
import traceback
from pathlib import Path

from rdfeval.harness import _exec_ldpy, _exec_python, _emit, graphs_isomorphic

TESTS = [
    "test_required_field_raises",
    "test_irifield_create",
    "test_irifield_convert_to_rdf",
    "test_irifield_convert_to_rdf_none",
    "test_irifield_convert_to_rdf_list_value",
    "test_irifield_convert_to_rdf_list_value_raises",
]


def run_tests(ns: dict) -> tuple[dict, object]:
    """Call each test_* in file order; fresh Database registry first."""
    Database = ns["Database"]
    Database.databases = {"default": None}
    outcomes = {}
    for name in TESTS:
        fn = ns[name]
        buf = io.StringIO()
        try:
            with contextlib.redirect_stdout(buf):
                fn()
            outcomes[name] = ("ok", None, buf.getvalue())
        except Exception as e:  # noqa: BLE001 - the outcome IS the datum
            outcomes[name] = ("raised", type(e).__name__, buf.getvalue())
    db = Database.databases.get("default")
    final_graph = db.g if db is not None else None
    return outcomes, final_graph


def main() -> dict:
    ex_dir = Path(__file__).resolve().parent
    verdict: dict = {"example": ex_dir.name, "equivalent": False,
                     "method": "custom:pytest-functions", "diffs": [],
                     "error": None}
    try:
        ns_o, out_o = _exec_python(ex_dir / "original.py")
        ns_t, out_t = _exec_ldpy(ex_dir / "translated.ldpy")
    except Exception:
        verdict["error"] = traceback.format_exc(limit=8)
        _emit(verdict)
        return verdict

    diffs: list[str] = []
    if out_o != out_t:
        diffs.append("stdout differs at module definition time")

    outcomes_o, graph_o = run_tests(ns_o)
    outcomes_t, graph_t = run_tests(ns_t)

    for name in TESTS:
        so, eo, bufo = outcomes_o[name]
        st, et, buft = outcomes_t[name]
        if (so, eo) != (st, et):
            diffs.append(f"{name}: outcome differs "
                         f"(original {so}/{eo} vs translated {st}/{et})")
        if bufo != buft:
            diffs.append(f"{name}: stdout differs during the call")

    if (graph_o is None) != (graph_t is None):
        diffs.append("final default-database graph presence differs")
    elif graph_o is not None and not graphs_isomorphic(graph_o, graph_t):
        diffs.append(f"final default-database graph: not isomorphic "
                     f"({len(graph_o)} vs {len(graph_t)} triples)")

    verdict["tests"] = list(TESTS)
    verdict["outcomes"] = {name: outcomes_o[name][:2] for name in TESTS}
    verdict["diffs"] = diffs
    verdict["equivalent"] = not diffs
    _emit(verdict)
    return verdict


VERDICT = main()

if __name__ == "__main__":
    sys.exit(0 if VERDICT["equivalent"] else 1)
