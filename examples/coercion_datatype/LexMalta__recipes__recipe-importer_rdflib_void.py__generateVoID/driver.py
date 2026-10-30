"""Validation driver for LexMalta__recipes__recipe-importer_rdflib_void.py__generateVoID.

The region is a module-level loop (the class-partition pass of rdflib's
generateVoID) that writes into the module graph `res`, so the oracle is
module state, as `run_pair(entry=None)` computes it: every module-level
graph by RDF isomorphism, every other module-level value both sides
define, and printed output.  On top of that, each prefix binding of the
original's `res` must be present in the translation's `res` (`@graph res`
may add the block's prefixes, never drop or rebind one the original has).

The module is run twice:

  1. as written: `distinctForPartitions = True`, the repository's default,
     with a class whose count and property sets are zero (0 coerced by the
     bare interpolation) beside one with several of each;
  2. with that one context line changed to `distinctForPartitions = False`
     (the function's keyword argument in the repository), on temporary
     copies of both artefacts.  Without this run the `if
     distinctForPartitions:` branch is only ever taken, and forcing the
     guard to `True` in the translation stays green.

Each artefact is the one RDFEVAL_SIDES names, so the same driver proves the
optimized artefacts; the copies keep the artefact's file name.
"""
import shutil
import tempfile
import traceback
from pathlib import Path

from rdfeval.harness import (
    _compare_value, _emit, _exec_artefact, _graphs, _values, sides_from_env,
)

HERE = Path(__file__).resolve().parent
CONTEXT_LINE = "distinctForPartitions = True\n"


def run_side(name: str, substitute: tuple[str, str] | None):
    """Execute one artefact, as is or on a copy with one line replaced."""
    if substitute is None:
        return _exec_artefact(HERE / name, f"__{name}__")
    old, new = substitute
    text = (HERE / name).read_text()
    if text.count(old) != 1:
        raise RuntimeError(f"{name}: context line {old!r} not found once")
    work = Path(tempfile.mkdtemp(prefix="void-partitions-"))
    try:
        copy = work / name
        copy.write_text(text.replace(old, new))
        return _exec_artefact(copy, f"__{name}__")
    finally:
        shutil.rmtree(work, ignore_errors=True)


def compare(label: str, left: str, right: str, substitute, diffs: list[str]):
    ns_o, out_o = run_side(left, substitute)
    ns_t, out_t = run_side(right, substitute)
    go, gt = _graphs(ns_o), _graphs(ns_t)
    if set(go) != set(gt):
        diffs.append(f"{label}: graph variables differ: {sorted(go)} vs {sorted(gt)}")
    for name in sorted(set(go) & set(gt)):
        _compare_value(go[name], gt[name], f"{label}: graph {name}", diffs)
        bound_t = set(gt[name].namespaces())
        lost = sorted(b for b in go[name].namespaces() if b not in bound_t)
        if lost:
            diffs.append(f"{label}: graph {name}: prefix bindings lost {lost}")
    vo, vt = _values(ns_o), _values(ns_t)
    for name in sorted(set(vo) & set(vt)):
        _compare_value(vo[name], vt[name], f"{label}: value {name}", diffs, True)
    if out_o != out_t:
        diffs.append(f"{label}: stdout differs")
    if not go or not any(len(g) for g in go.values()):
        diffs.append(f"{label}: the original's graphs are empty")
    return sorted(set(go) & set(gt)), sorted(set(vo) & set(vt))


def main() -> dict:
    verdict: dict = {"example": HERE.name, "equivalent": False,
                     "method": "custom:module-state x2 (distinctForPartitions True/False)",
                     "diffs": [], "error": None}
    diffs: list[str] = []
    try:
        left, right = sides_from_env()
        graphs, values = compare("as written", left, right, None, diffs)
        compare("distinctForPartitions = False", left, right,
                (CONTEXT_LINE, "distinctForPartitions = False\n"), diffs)
    except Exception:
        verdict["error"] = traceback.format_exc(limit=8)
        _emit(verdict)
        return verdict
    verdict["graphs_compared"] = graphs
    verdict["values_compared"] = values
    verdict["diffs"] = diffs
    verdict["equivalent"] = not diffs
    _emit(verdict)
    return verdict


VERDICT = main()
