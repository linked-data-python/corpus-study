"""Validation driver for
statnett__KGraphPy__kgraphpy_header.py__CIMMetadataHeader_from_manifest.

Not the generic ``run_pair(entry=..., calls=[...])`` shape: one of the two
cases the fixture is required to cover -- the zero-solution graph identifier
-- makes ``from_manifest`` *raise* ``ValueError``, and ``run_pair``'s call
loop treats any exception as a driver bug (it aborts the whole verdict with
a traceback) rather than as a per-case outcome to compare. So this driver
calls the entry point itself, on both sides, and records "returned X" or
"raised Y" the way the edmondchuc__rdflib-orm driver in this same stratum
does for its five pytest functions.

Equality of the two ``CIMMetadataHeader`` instances the matching case
returns is judged by ``__eq__`` on the shim class in original.py/
translated.ldpy (subject equality plus set-equality of the header graph's
triples) -- both sides define that method identically, so it adds no
asymmetric behaviour, only comparability for a plain object the generic
harness would otherwise compare by identity.
"""
from pathlib import Path

from rdfeval.harness import _exec_ldpy, _exec_python, _emit, fixture_graph

FIXTURE = Path(__file__).resolve().parent / "fixture.ttl"


def call(fn, graph_uri):
    try:
        return ("ok", fn(str(FIXTURE), graph_uri, "turtle"), None)
    except Exception as e:  # noqa: BLE001 - the outcome IS the datum
        return ("raised", None, type(e).__name__)


def main() -> dict:
    ex_dir = Path(__file__).resolve().parent
    verdict: dict = {"example": ex_dir.name, "equivalent": False,
                     "method": "custom:from_manifest-outcomes", "diffs": [],
                     "error": None}
    try:
        ns_o, out_o = _exec_python(ex_dir / "original.py")
        ns_t, out_t = _exec_ldpy(ex_dir / "translated.ldpy")
    except Exception:
        import traceback
        verdict["error"] = traceback.format_exc(limit=8)
        _emit(verdict)
        return verdict

    diffs: list[str] = []

    cases = {
        "matching": "urn:uuid:graph-1",
        "zero-solution": "urn:uuid:no-such-graph",
    }
    for name, graph_uri in cases.items():
        so, ro, eo = call(ns_o["from_manifest"], graph_uri)
        st, rt, et = call(ns_t["from_manifest"], graph_uri)
        if (so, eo) != (st, et):
            diffs.append(f"{name}: outcome differs "
                         f"(original {so}/{eo} vs translated {st}/{et})")
        elif so == "ok" and ro != rt:
            diffs.append(f"{name}: result differs "
                         f"(subject {ro.subject!r} vs {rt.subject!r}, "
                         f"{len(ro.graph)} vs {len(rt.graph)} triples)")

    if out_o != out_t:
        diffs.append("stdout differs at module definition time")

    verdict["cases"] = list(cases)
    verdict["diffs"] = diffs
    verdict["equivalent"] = not diffs
    _emit(verdict)
    return verdict


VERDICT = main()

if __name__ == "__main__":
    import sys
    sys.exit(0 if VERDICT["equivalent"] else 1)
