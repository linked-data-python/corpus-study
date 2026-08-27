"""Execution/comparison helpers used by example validation drivers.

A driver calls :func:`run_pair`, which

  1. executes ``original.py`` and ``translated.ldpy`` (through the ldpy
     transpiler) in two fresh module namespaces, capturing stdout;
  2. either compares *module state* (every rdflib Graph in the globals,
     paired by variable name, plus non-graph variables both modules define),
     or — when ``entry`` names a function — calls it with each fixture in
     ``calls`` and compares the results;
  3. graph comparison is rdflib graph isomorphism (``rdflib.compare``),
     never raw serialisation; other values are normalised
     (term-by-term for lists/tuples/sets/dicts) then compared for equality.

The verdict is a JSON-serialisable dict; drivers print it so the validate
stage can collect it from a subprocess.
"""

from __future__ import annotations

import contextlib
import io
import json
import sys
import traceback
from pathlib import Path


def _exec_python(path: Path) -> tuple[dict, str]:
    ns: dict = {"__name__": "__original__", "__file__": str(path)}
    out = io.StringIO()
    code = compile(path.read_text(), str(path), "exec")
    with contextlib.redirect_stdout(out):
        exec(code, ns)
    return ns, out.getvalue()


def _exec_ldpy(path: Path) -> tuple[dict, str]:
    from ldpy.transpiler import transpile
    r = transpile(path.read_text(), filename=str(path))
    ns: dict = {"__name__": "__translated__", "__file__": str(path)}
    out = io.StringIO()
    code = compile(r.code, str(path), "exec")
    with contextlib.redirect_stdout(out):
        exec(code, ns)
    return ns, out.getvalue()


def _graphs(ns: dict) -> dict[str, object]:
    from rdflib import Graph
    return {k: v for k, v in ns.items()
            if isinstance(v, Graph) and not k.startswith("_")}


def graphs_isomorphic(g1, g2) -> bool:
    from rdflib.compare import to_isomorphic
    return to_isomorphic(g1) == to_isomorphic(g2)


def normalise(value):
    """Make values comparable across the two runs (BNode ids differ)."""
    from rdflib import BNode, Graph
    if isinstance(value, Graph):
        from rdflib.compare import to_isomorphic
        return ("graph", to_isomorphic(value).graph_digest())
    if isinstance(value, BNode):
        return ("bnode",)
    if isinstance(value, dict):
        return {k: normalise(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [normalise(v) for v in value]
    if isinstance(value, set):
        return sorted(map(repr, (normalise(v) for v in value)))
    return value


def _compare_value(a, b, label: str, diffs: list[str]) -> None:
    from rdflib import Graph
    if isinstance(a, Graph) and isinstance(b, Graph):
        if not graphs_isomorphic(a, b):
            diffs.append(f"{label}: graphs not isomorphic "
                         f"({len(a)} vs {len(b)} triples)")
        return
    try:
        equal = normalise(a) == normalise(b)
    except Exception as e:
        diffs.append(f"{label}: comparison error {e}")
        return
    if not equal:
        diffs.append(f"{label}: values differ ({a!r} vs {b!r})")


def run_pair(driver_file: str, entry: str | None = None,
             calls: list | None = None) -> dict:
    ex_dir = Path(driver_file).resolve().parent
    verdict: dict = {"example": ex_dir.name, "equivalent": False,
                     "method": None, "diffs": [], "error": None}
    try:
        ns_o, out_o = _exec_python(ex_dir / "original.py")
        ns_t, out_t = _exec_ldpy(ex_dir / "translated.ldpy")
    except Exception:
        verdict["error"] = traceback.format_exc(limit=8)
        _emit(verdict)
        return verdict

    diffs: list[str] = []
    if entry:
        verdict["method"] = f"entry:{entry}"
        fo, ft = ns_o.get(entry), ns_t.get(entry)
        if not callable(fo) or not callable(ft):
            verdict["error"] = f"entry {entry!r} not found in both modules"
            _emit(verdict)
            return verdict
        if not calls:
            verdict["error"] = "no fixtures: provide calls=[(args, kwargs), …]"
            _emit(verdict)
            return verdict
        for i, (args, kwargs) in enumerate(calls):
            try:
                ro = fo(*args, **kwargs)
                rt = ft(*args, **kwargs)
            except Exception:
                verdict["error"] = traceback.format_exc(limit=8)
                _emit(verdict)
                return verdict
            _compare_value(ro, rt, f"call[{i}]", diffs)
        verdict["calls"] = len(calls)
    else:
        verdict["method"] = "module-state"
        go, gt = _graphs(ns_o), _graphs(ns_t)
        if set(go) != set(gt):
            diffs.append(f"graph variables differ: {sorted(go)} vs {sorted(gt)}")
        for name in sorted(set(go) & set(gt)):
            _compare_value(go[name], gt[name], f"graph {name}", diffs)
        if out_o != out_t:
            diffs.append("stdout differs")
        verdict["graphs_compared"] = sorted(set(go) & set(gt))
        if not (go or gt) and out_o == out_t == "":
            diffs.append("nothing observable to compare")
    verdict["diffs"] = diffs
    verdict["equivalent"] = not diffs
    _emit(verdict)
    return verdict


def _emit(verdict: dict) -> None:
    print("RDFEVAL-VERDICT " + json.dumps(verdict), file=sys.stderr)
