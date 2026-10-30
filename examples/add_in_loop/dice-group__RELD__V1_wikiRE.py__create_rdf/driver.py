"""Validation driver for dice-group__RELD__V1_wikiRE.py__create_rdf.

Establishes semantic equivalence of original.py and translated.ldpy.

The region is the body of one iteration of create_rdf's loop over the
relations (V1/wikiRE.py:192-198): `nyt` is read from rel_data for the
current relation, and the owl:sameAs triple is written only if
`str(nyt) != 'nan'`.  Its context (nyt, relation, rel_data) comes from
context_shim.py.  What it decides is the graph `g`, and whether it raises.

Runs, and what each decides:

  A nominal -- run_pair's module-state comparison, unchanged: the shim's
    P19 row ("place of birth"), whose RE-NYT-Relation is 'place_of_birth',
    so the guard is true and one triple is written (graph by isomorphism,
    module values, stdout).
  B nan (repair of 2026-10-30) -- the P569 row ("date of birth"), whose
    RE-NYT-Relation is blank in the real AllRelationWithCrossCheck.csv:
    `nyt` is computed as the repository computes it (wikiRE.py:192), so it
    is the float NaN pd.read_csv gives for a blank cell, and `relation` is
    res+"R-"+str(Wrid).  The guard is false: nothing is written.  Without
    this run, the guard forced to `True`, or rewritten as `if nyt:` (NaN is
    truthy), stayed green; both now raise IndexError on the translation
    side (the second .loc lookup is empty) where the original writes
    nothing.

For B, each side runs with a context_shim module built here (the real shim,
re-imported fresh, with nyt and relation of the P569 row), and the driver
compares the outcome (a raise, by type and message), the graph `g` by
isomorphism, and the prefix bindings of `g` (every binding of the
original's must be in the translation's; `@graph g` adds the block's own,
record ldpy/027).  The bindings are also compared for A.

Mutants killed (each in a copy of the pair): `+{ }` removed, subject or
object widened to `[]`, object interpolated as a plain str (a Literal),
guard forced to `False` (by A); guard forced to `True`, guard rewritten
`if nyt:` (by B only).
"""
import contextlib
import importlib
import io
import sys
from pathlib import Path

from rdfeval import harness
from rdfeval.harness import run_pair

HERE = Path(__file__).resolve().parent
RES = "https://reld.dice-research.org/resource/"


def _fresh_shim(rel=None):
    """The real context_shim, re-imported; for `rel`, nyt and relation are
    those of that row, read as wikiRE.py:133 and :192 read them."""
    sys.modules.pop("context_shim", None)
    if str(HERE) not in sys.path:
        sys.path.insert(0, str(HERE))
    shim = importlib.import_module("context_shim")
    if rel is not None:
        rd = shim.rel_data
        shim.nyt = rd.loc[rd['WikidataIds'] == rel, 'RE-NYT-Relation'].iloc[0]
        shim.relation = RES + "R-" + str(rd.loc[rd['WikidataIds'] == rel,
                                                 'Wrid'].iloc[0])
    return shim


def _run(path, execute, rel):
    _fresh_shim(rel)
    try:
        ns, out = execute(path)
    except Exception as e:                        # noqa: BLE001 - compared
        return harness.Raised(e), None, ""
    return None, ns["g"], out


def _bindings(g):
    return {(p, str(n)) for p, n in g.namespaces()}


def _compare(label, rel, diffs):
    ro, go, oo = _run(HERE / "original.py", harness._exec_python, rel)
    rt, gt, ot = _run(HERE / "translated.ldpy", harness._exec_ldpy, rel)
    if ro != rt:
        diffs.append(f"{label}: outcome differs ({ro!r} vs {rt!r})")
        return
    if ro is not None:
        return
    harness._compare_value(go, gt, f"{label}: graph g", diffs)
    missing = sorted(_bindings(go) - _bindings(gt))
    if missing:
        diffs.append(f"{label}: prefix bindings of the original missing "
                     f"from the translation: {missing}")
    if oo != ot:
        diffs.append(f"{label}: stdout differs")


# A. run_pair's verdict, kept whole; its own RDFEVAL-VERDICT line is held
#    back so that a single verdict, with the runs below folded in, is
#    emitted at the end.
_fresh_shim()
with contextlib.redirect_stderr(io.StringIO()):
    VERDICT = run_pair(__file__, entry=None, calls=None)

if VERDICT.get("error") is None:
    try:
        _compare("A nominal (P19)", None, VERDICT["diffs"])
        _compare("B nan (P569)", "P569", VERDICT["diffs"])
        VERDICT["extra_runs"] = ["A bindings", "B nan (P569)"]
    except Exception as e:                        # noqa: BLE001 - reported
        VERDICT["error"] = f"extra runs: {type(e).__name__}: {e}"
    VERDICT["equivalent"] = not VERDICT["diffs"] and VERDICT["error"] is None

harness._emit(VERDICT)
