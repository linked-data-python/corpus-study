"""Validation driver for altunelyusuf__SemanticTechnologies__landscape_07-tooling_build_core_v6_3_0.py__<module>_162.

Establishes semantic equivalence of original.py and translated.ldpy.

The region is module-level code over a constant input (the eight
NEW_RELATIONS of the verbatim enrichment_n_v6_0_0.py), so it has one run,
and that run is decided entirely by what it writes into `g2`:

  * the triples of `g2`, by isomorphism -- run_pair's module-state
    comparison, unchanged (it also compares the module-level values both
    sides define, and stdout);
  * the prefix bindings of `g2` (repair of 2026-10-30).  The repository
    parses the real tbox, whose header binds `semtech:` to the
    `http://example.org/semtech#` namespace, and serialises `g2` later
    (build_core_v6_3_0.py:207), so the region must leave that binding in
    place.  The placeholder tbox used to declare `sem:` itself, which hid
    the rebinding; it now carries the real file's eight prefix lines
    verbatim.  Every binding of the original's `g2` must be in the
    translation's (`@graph` adds the block's own prefixes, record
    ldpy/027: extra bindings are tolerated).

Mutants killed (each in a copy of the pair): `+{ }` removed, subject or
object widened to `[]`, predicate made constant, the last row dropped, the
object taken from the subject column; and, by the binding check only, a
`@prefix sem:` whose name differs from the tbox's `semtech:` (the
`@graph g2` rebinding replaces `semtech:`).
"""
import contextlib
import io
import sys
from pathlib import Path

from rdfeval import harness
from rdfeval.harness import run_pair

HERE = Path(__file__).resolve().parent
SHIMS = ("context_predecl",)


def _fresh_shims():
    for name in SHIMS:
        sys.modules.pop(name, None)


def _bindings(ns):
    return {(p, str(n)) for p, n in ns["g2"].namespaces()}


# 1. run_pair's verdict (triples, values, stdout), kept whole; its own
#    RDFEVAL-VERDICT line is held back so that a single verdict, with the
#    binding check folded in, is emitted below.
_fresh_shims()
with contextlib.redirect_stderr(io.StringIO()):
    VERDICT = run_pair(__file__, entry=None, calls=None)

# 2. the prefix bindings of g2, on a second run of each side.
if VERDICT.get("error") is None:
    try:
        _fresh_shims()
        ns_o, _ = harness._exec_python(HERE / "original.py")
        _fresh_shims()
        ns_t, _ = harness._exec_ldpy(HERE / "translated.ldpy")
        missing = sorted(_bindings(ns_o) - _bindings(ns_t))
        if missing:
            VERDICT["diffs"].append(
                f"graph g2: prefix bindings of the original missing "
                f"from the translation: {missing}")
        VERDICT["bindings_compared"] = True
    except Exception as e:                        # noqa: BLE001 - reported
        VERDICT["error"] = f"binding check: {type(e).__name__}: {e}"
    VERDICT["equivalent"] = not VERDICT["diffs"] and VERDICT["error"] is None

harness._emit(VERDICT)
