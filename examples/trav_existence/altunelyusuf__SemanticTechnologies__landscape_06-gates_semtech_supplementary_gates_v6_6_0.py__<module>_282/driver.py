"""Validation driver for altunelyusuf__SemanticTechnologies__landscape_06-gates_semtech_supplementary_gates_v6_6_0.py__<module>_282.

The region is module-level script code: it reads `HERE` and `feats` from
the shim, parses `{HERE}/08-agents/agents_backlog_abox_v4_1_0.ttl`, and
leaves `done` (features with b2:hasState b2:Done) and `ev_ok` (every Done
feature has some b2:hasEvidence) in module globals. Each run compares, as
`run_pair(entry=None)` does, every graph and every comparable module value
the two sides share (module-state oracle).

One fixture cannot prove both islands: with the shim's data `ev_ok` is
False by construction, so a wrong predicate in the b2:hasEvidence island
went unseen. The driver therefore executes both sides once per scenario,
pointing the shim's `HERE` at the scenario directory and setting `feats`
the way the repository builds it (landscape/06-gates/
semtech_supplementary_gates_v6_6_0.py:279,
`feats = list(gbk.subjects(RDF.type, B2.Feature))`, URIRefs):

- `base`           the shim as shipped (F1 Done+evidence, F2 Done without,
                   F3 not Done with evidence, F4 bare): done=[F1, F2],
                   ev_ok False. Kills the evidence predicate widened to `?p`.
- `evidenced`      every Done feature has evidence (one as the falsy
                   literal "", one with two values), plus F5 carrying
                   b2:Done under another predicate and a non-feature with
                   evidence: ev_ok True. Kills hasEvidence replaced by
                   another predicate, and hasState widened to `?p`.
- `other_evidence` the only Done feature has a proof under another
                   predicate while a non-Done feature has b2:hasEvidence:
                   ev_ok False. Kills the evidence subject widened.
- `no_done`        no feature is Done (b2:Done sits on a non-feature): done
                   is empty, ev_ok True. Kills the Done subject widened.

The shim module is shared by both sides; it holds only the two inputs,
which the driver resets before each side runs.
"""
from __future__ import annotations

import traceback
from pathlib import Path

from rdflib import Graph, Namespace, RDF

from rdfeval.harness import (_compare_value, _emit, _exec_ldpy, _exec_python,
                             _graphs, _values)

HERE = Path(__file__).resolve().parent
B2 = Namespace("http://example.org/backlog#")
FIXTURE = "08-agents/agents_backlog_abox_v4_1_0.ttl"

import shim  # noqa: E402  (the region's own context module)

BASE = (shim.HERE, list(shim.feats))


def _scenario(name):
    if name == "base":
        return BASE
    here = str(HERE / "scenarios" / name)
    g = Graph().parse(f"{here}/{FIXTURE}")
    return here, list(g.subjects(RDF.type, B2.Feature))


def _run(execute, path, label, scenario):
    shim.HERE, feats = _scenario(scenario)
    shim.feats = list(feats)
    return execute(path, label)


verdict = {"example": HERE.name, "equivalent": False,
           "method": "module-state per scenario", "diffs": [], "error": None}
diffs: list[str] = []
compared: dict[str, list[str]] = {}
try:
    for scenario in ("base", "evidenced", "other_evidence", "no_done"):
        ns_o, out_o = _run(_exec_python, HERE / "original.py",
                           "__original__", scenario)
        ns_t, out_t = _run(_exec_ldpy, HERE / "translated.ldpy",
                           "__translated__", scenario)
        go, gt = _graphs(ns_o), _graphs(ns_t)
        if set(go) != set(gt):
            diffs.append(f"[{scenario}] graph variables differ: "
                         f"{sorted(go)} vs {sorted(gt)}")
        for name in sorted(set(go) & set(gt)):
            _compare_value(go[name], gt[name], f"[{scenario}] graph {name}",
                           diffs)
        vo, vt = _values(ns_o), _values(ns_t)
        shared = sorted(set(vo) & set(vt))
        for name in shared:
            _compare_value(vo[name], vt[name], f"[{scenario}] value {name}",
                           diffs)
        for name in ("done", "ev_ok"):
            if name not in shared:
                diffs.append(f"[{scenario}] {name} not compared")
        if out_o != out_t:
            diffs.append(f"[{scenario}] stdout differs")
        compared[scenario] = shared
    verdict["values_compared"] = compared
    verdict["names_only_original"] = sorted(set(vo) - set(vt))
    verdict["diffs"] = diffs
    verdict["equivalent"] = not diffs
except Exception:
    verdict["error"] = traceback.format_exc(limit=8)
finally:
    shim.HERE, shim.feats = BASE[0], list(BASE[1])

_emit(verdict)
VERDICT = verdict
