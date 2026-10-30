"""Validation driver for Haoyu-R__SeLoC-ML__tflite2semantic_parser_xlsx.py__tflite2semantic.

The region is the tail of the per-layer if/elif/else of the loop
``for j in range(graph.OperatorsLength())`` of tflite2semantic() (see
tflite2semantic_parser_xlsx.py:209).  The real repository reaches all three
branches: j == 0 (input layer), 0 < j < OperatorsLength() - 1 (middle layer)
and j == OperatorsLength() - 1 (output layer), and a one-operator model
(OperatorsLength() == 1) takes the input branch only, since ``j == 0`` is
tested first.  A module-state run executes the region once, with the j and
graph of context_shim; the shim pins one pair, which leaves two of the three
branches (4 of the 7 ``+{ }``) never executed.

So this driver executes both sides once per scenario (j, OperatorsLength()),
setting those two shim attributes before each module run, and compares for
each scenario:

  * the graph ``g`` (isomorphism);
  * the sequence of addCommonInfo calls the region makes (layer IRI and
    keyword flags).  The shim's addCommonInfo is replaced here by a recorder
    that writes nothing to g, so it cannot manufacture a match; what the
    region passes to it (which layer, input_layer/output_layer) is part of
    the region's observable behaviour and is compared.

Scenarios: j = 0 of 10 (first), j = 1 of 10 and j = 5 of 10 and j = 8 of 10
(middle layers, different indices), j = 9 of 10 (last), j = 0 of 1 (single
operator: the input branch wins over the output branch), j = 1 of 2 (last of
two).  j is always an int, as range() yields it.

Mutants of translated.ldpy run in copies of the region directory, with this
driver: see meta.json "repair" for the list.
"""
import json
import sys
import traceback
from pathlib import Path

from rdfeval import harness

import context_shim

ex_dir = Path(__file__).resolve().parent

SCENARIOS = [  # (j, graph.OperatorsLength())
    (0, 10), (1, 10), (5, 10), (8, 10), (9, 10), (0, 1), (1, 2),
]

_calls: list = []


def _record(layer, input_layer=False, output_layer=False):
    _calls.append((str(layer), input_layer, output_layer))


class _Subgraph:
    def __init__(self, n):
        self.n = n

    def OperatorsLength(self):
        return self.n


def _run(runner, path, j, n):
    context_shim.j = j
    context_shim.graph = _Subgraph(n)
    context_shim.addCommonInfo = _record
    del _calls[:]
    ns, out = runner(path)
    return ns, out, list(_calls)


verdict: dict = {"example": ex_dir.name, "equivalent": False,
                 "method": "module-state x %d scenarios (j, OperatorsLength)"
                           % len(SCENARIOS),
                 "diffs": [], "error": None}
try:
    diffs: list = []
    for j, n in SCENARIOS:
        tag = f"j={j}/n={n}"
        ns_o, out_o, calls_o = _run(harness._exec_python,
                                    ex_dir / "original.py", j, n)
        ns_t, out_t, calls_t = _run(harness._exec_ldpy,
                                    ex_dir / "translated.ldpy", j, n)
        g_o, g_t = ns_o["g"], ns_t["g"]
        if not len(g_o):
            diffs.append(f"{tag}: the original wrote nothing to g")
        harness._compare_value(g_o, g_t, f"{tag} graph g", diffs)
        if calls_o != calls_t:
            diffs.append(f"{tag}: addCommonInfo calls differ "
                         f"({calls_o!r} vs {calls_t!r})")
        if len(calls_o) != 1:
            diffs.append(f"{tag}: expected exactly one addCommonInfo call, "
                         f"got {len(calls_o)}")
        if out_o != out_t:
            diffs.append(f"{tag}: stdout differs")
    verdict["diffs"] = diffs
    verdict["equivalent"] = not diffs
except Exception:
    verdict["error"] = traceback.format_exc(limit=8)

harness._emit(verdict)
VERDICT = verdict
