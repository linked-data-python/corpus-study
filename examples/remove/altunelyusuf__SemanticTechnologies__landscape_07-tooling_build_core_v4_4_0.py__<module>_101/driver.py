"""Validation driver for altunelyusuf__SemanticTechnologies__landscape_07-tooling_build_core_v4_4_0.py__<module>_101.

The region is a module-level statement that wipes the corpus node's skos:note
before the script re-states a fresh scorecard, so the oracle is module state:
both representations parse the same fixture
(01-research/semtech_research_v4_3_0.ttl, see meta.json) into a fresh graph `g1`
and the region is decided by what it leaves in `g1`:

  * the triples of `g1`, by isomorphism -- run_pair's module-state
    comparison, unchanged.  The fixture gives the corpus two notes (the object
    wildcard takes both) and gives its publications notes of their own (a
    pattern that did not pin the subject would take those too);
  * the prefix bindings of `g1` (audit of 2026-10-31).  The repository
    serialises `g1` right after the region (build_core_v4_4_0.py:113), with
    the bindings the parse took from the real file's header, which the fixture
    now carries verbatim.  `@graph g1` binds the block's prefixes on `g1`
    (record ldpy/027), so a block prefix whose name differs from the file's
    for the same namespace would replace the file's binding: every binding of
    the original's `g1` must be in the translation's (extra ones tolerated).

Mutants killed (each in a copy of the pair): the island removed or matching
nothing, the subject widened to `?c`, the predicate widened to `?p`, the
object bound to one literal, the subject coerced from a `str`; and, by the
binding check only, `@prefix sk:` for the SKOS namespace (it rebinds the
file's `skos:`).  Equivalent, not counted: `-{ … }(g1)` without `@graph`,
since `skos:` is already bound to the same namespace on `g1`.
"""
import contextlib
import io
import sys
from pathlib import Path

from rdfeval import harness
from rdfeval.harness import run_pair

HERE = Path(__file__).resolve().parent
SHIMS = ("research_context",)
GRAPH = "g1"


def _fresh_shims():
    for name in SHIMS:
        sys.modules.pop(name, None)


def _bindings(ns):
    return {(p, str(n)) for p, n in ns[GRAPH].namespaces()}


# 1. run_pair's verdict (triples, values, stdout), kept whole; its own
#    RDFEVAL-VERDICT line is held back so that a single verdict, with the
#    binding check folded in, is emitted below.
_fresh_shims()
with contextlib.redirect_stderr(io.StringIO()):
    VERDICT = run_pair(__file__, entry=None, calls=None)

# 2. the prefix bindings of g1, on a second run of each side.
if VERDICT.get("error") is None:
    try:
        _fresh_shims()
        ns_o, _ = harness._exec_python(HERE / "original.py")
        _fresh_shims()
        ns_t, _ = harness._exec_ldpy(HERE / "translated.ldpy")
        missing = sorted(_bindings(ns_o) - _bindings(ns_t))
        if missing:
            VERDICT["diffs"].append(
                f"graph {GRAPH}: prefix bindings of the original missing "
                f"from the translation: {missing}")
        VERDICT["bindings_compared"] = True
    except Exception as e:                        # noqa: BLE001 - reported
        VERDICT["error"] = f"binding check: {type(e).__name__}: {e}"
    VERDICT["equivalent"] = not VERDICT["diffs"] and VERDICT["error"] is None

harness._emit(VERDICT)
