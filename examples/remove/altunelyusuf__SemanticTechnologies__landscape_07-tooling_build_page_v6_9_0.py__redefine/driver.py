"""Validation driver for altunelyusuf__SemanticTechnologies__landscape_07-tooling_build_page_v6_9_0.py__redefine.

redefine() takes no graph: it mutates the module-level `g` that the region's
preamble parses.  entry=None therefore compares module state — `g` after the
calls replayed by the context shim — by RDF isomorphism.  The stand-in ABox
(04-page/semtech_page_abox_v6_8_0.ttl) carries two rdfs:label values on one
subject, so a `-{ }` that did not wildcard would leave a stale label behind
and the graphs would not be isomorphic.

Audit of 2026-10-31 — a second run of each side, after the replay, checks
what that run leaves out:

  * the calls the repository really makes (build_page_v6_9_0.py:66-73):
    sp:Page and sp:Doc with label= and defn=, sp:ReferencesRegion with defn=
    only, on the three subjects as the stand-in ABox carries them;
  * the falsy string: redefine(sp:Doc, note="", scope="") and
    redefine(sp:ReferencesRegion, label="", defn="").  The guard is
    `is not None`, so "" removes the old values and writes an empty @en
    literal; a guard weakened to truthiness skips both, and only these calls
    show it;
  * the prefix bindings of `g`.  The repository serialises `g` after the
    region (build_page_v6_9_0.py:106) with the bindings the parse took from
    the real header, which the stand-in now carries verbatim; `@graph g`
    binds the block's prefixes on `g` (record ldpy/027), so a block prefix
    named differently from the file's for the same namespace would replace
    the file's binding.  Every binding of the original's `g` must be in the
    translation's (extra ones tolerated).

Mutants killed (each in a copy of the pair), for each of the four branches:
the guard forced True or False, the guard weakened to truthiness (by the
falsy calls only), the `-{ }` removed or its subject widened, the `+{ }`
removed, `@en` dropped; and `@prefix sk:` / `@prefix rs:` for SKOS / RDFS
(by the binding check only).  Equivalent, not counted: the `@graph g`
dropped for a `(g)` call suffix on every island, since every block prefix
is already bound to the same namespace on `g`.
"""
import contextlib
import io
import sys
from pathlib import Path

from rdflib import Namespace

from rdfeval import harness
from rdfeval.harness import run_pair

HERE = Path(__file__).resolve().parent
SHIMS = ("context_shim",)
SP = Namespace("http://example.org/semtech/page#")

# (iri, kwargs) -- the real calls first, shortened texts, then the falsy ones
CALLS = [
    (SP.Page, {"label": "Taxonomies of Semantic Technologies — conversational "
                        "interactive landscape page v6.9.0",
               "defn": "This page is the Stage-4 conversational rendering of "
                       "the v4.0.0 landscape."}),
    (SP.ReferencesRegion, {"defn": "The references region lists all "
                                   "ninety-nine verified or flagged registry "
                                   "entries with levels."}),
    (SP.Doc, {"label": "Semantic technology landscape report (Stage-3 "
                       "document, v6.9.0)",
              "defn": "This source document is the deepened Stage-3 report."}),
    (SP.Doc, {"note": "", "scope": ""}),
    (SP.ReferencesRegion, {"label": "", "defn": ""}),
]


def _fresh_shims():
    for name in SHIMS:
        sys.modules.pop(name, None)


def _bindings(graph):
    return {(p, str(n)) for p, n in graph.namespaces()}


def _side(exec_fn, path):
    _fresh_shims()
    ns, _ = exec_fn(path)
    outcomes = [harness._outcome(ns["redefine"], (iri,), kw) for iri, kw in CALLS]
    return ns["g"], outcomes


# 1. run_pair's verdict (module state after the shim's replay), kept whole;
#    its own RDFEVAL-VERDICT line is held back so that a single verdict is
#    emitted below.
_fresh_shims()
with contextlib.redirect_stderr(io.StringIO()):
    VERDICT = run_pair(__file__, entry=None, calls=None)

# 2. the real calls, the falsy calls and the bindings, on a second run.
if VERDICT.get("error") is None:
    try:
        g_o, out_o = _side(harness._exec_python, HERE / "original.py")
        g_t, out_t = _side(harness._exec_ldpy, HERE / "translated.ldpy")
        for i, (ro, rt) in enumerate(zip(out_o, out_t)):
            if ro != rt:
                VERDICT["diffs"].append(
                    f"extra call[{i}]: outcome differs ({ro!r} vs {rt!r})")
        if not harness.graphs_isomorphic(g_o, g_t):
            VERDICT["diffs"].append(
                f"graph g after the extra calls: not isomorphic "
                f"({len(g_o)} vs {len(g_t)} triples)")
        missing = sorted(_bindings(g_o) - _bindings(g_t))
        if missing:
            VERDICT["diffs"].append(
                f"graph g: prefix bindings of the original missing "
                f"from the translation: {missing}")
        VERDICT["extra_calls"] = len(CALLS)
        VERDICT["bindings_compared"] = True
    except Exception as e:                        # noqa: BLE001 - reported
        VERDICT["error"] = f"extra calls: {type(e).__name__}: {e}"
    VERDICT["equivalent"] = not VERDICT["diffs"] and VERDICT["error"] is None

harness._emit(VERDICT)
