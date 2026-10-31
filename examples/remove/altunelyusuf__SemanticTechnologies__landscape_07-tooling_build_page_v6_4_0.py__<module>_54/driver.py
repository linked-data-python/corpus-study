"""Validation driver for altunelyusuf__SemanticTechnologies__landscape_07-tooling_build_page_v6_4_0.py__<module>_54.

The region is a module-level statement that wipes three version stamps off the
ontology node, so the oracle is module state: both representations parse the
same fixture (04-page/semtech_page_abox_v6_3_0.ttl, see meta.json) into a fresh
graph `g`, and the region is decided by what it leaves in `g`:

  * the triples of `g`, by isomorphism -- run_pair's module-state comparison,
    unchanged.  Each of the three predicates carries two values on the
    ontology node (the object wildcard takes both), the node carries other
    predicates, and other subjects carry the same predicates (a pattern that
    did not pin the subject would take those too);
  * the prefix bindings of `g` (audit of 2026-10-31).  The repository
    serialises `g` after the region (build_page_v6_4_0.py:106), with the
    bindings the parse took from the real file's header, which the fixture
    now carries verbatim.  `@graph g` binds the block's prefixes on `g`
    (record ldpy/027), so a block prefix whose name differs from the file's
    for the same namespace would replace the file's binding: every binding of
    the original's `g` must be in the translation's (extra ones tolerated).

Mutants killed (each in a copy of the pair): the island removed, the subject
widened to `?s`, the predicate widened to `?q`, the object bound to "6.3.0",
each predicate dropped from the loop tuple, ONT moved to the neighbouring
ontology; and, by the binding check only, `@prefix dct:` for DCTERMS or
`@prefix ow:` for OWL (each rebinds the file's prefix).  Equivalent, not
counted: `-{ … }(g)` without `@graph`, since `owl:` and `dcterms:` are already
bound to the same namespaces on `g`.
"""
import contextlib
import io
import sys
from pathlib import Path

from rdfeval import harness
from rdfeval.harness import run_pair

HERE = Path(__file__).resolve().parent
SHIMS = ("page_context",)
GRAPH = "g"


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

# 2. the prefix bindings of g, on a second run of each side.
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
