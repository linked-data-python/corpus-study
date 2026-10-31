"""Validation driver for altunelyusuf__SemanticTechnologies__landscape_07-tooling_build_core_v6_9_0.py__<module>_101.

Establishes semantic equivalence of original.py and translated.ldpy.

A module-level region: both modules run top to bottom, and the driver
compares what run_pair(entry=None) compares --

  * every rdflib Graph in their globals (here g1), by isomorphism;
  * every other module-level value both sides define (corpus, RO_PUB, pub,
    key, e, ...);
  * what each side prints;

-- plus the one thing run_pair does not see: g1's PREFIX BINDINGS.  The
repository serialises g1 right after this region
(build_core_v6_9_0.py:120, `g1.serialize(..., format="turtle")`), and g1
comes from parsing semtech_research_v6_8_0.ttl, whose real header binds
`sr:` to http://example.org/semtech/research# (the stand-in carries that
header verbatim).  `@graph g1` binds the block's own prefixes on g1, and
rdflib's `bind()` REPLACES the prefix a namespace already has: a block
declaring `@prefix srns: <...research#>` makes the serialised file say
`srns:` where the repository writes `sr:`.  So every binding the original's
g1 carries must still be in the translation's; extra bindings are tolerated
(record ldpy/027).

The `[:180]` slice on the label is not exercised: no "cite" anywhere in the
repository's enrichment data exceeds 149 characters, so removing it has no
effect on any input the repository has.
"""
import json
import sys
from pathlib import Path

from rdfeval import harness

ex_dir = Path(__file__).resolve().parent
verdict: dict = {"example": ex_dir.name, "equivalent": False,
                 "method": "module-state (custom: graphs, shared values, "
                           "stdout, prefix bindings of g1)",
                 "diffs": [], "error": None}
try:
    ns_o, out_o = harness._exec_python(ex_dir / "original.py")
    ns_t, out_t = harness._exec_ldpy(ex_dir / "translated.ldpy")
    diffs: list[str] = []
    go, gt = harness._graphs(ns_o), harness._graphs(ns_t)
    if set(go) != set(gt):
        diffs.append(f"graph variables differ: {sorted(go)} vs {sorted(gt)}")
    for name in sorted(set(go) & set(gt)):
        harness._compare_value(go[name], gt[name], f"graph {name}", diffs)
        lost = set(go[name].namespaces()) - set(gt[name].namespaces())
        if lost:
            diffs.append(f"graph {name}: prefix bindings lost {sorted(lost)}")
    vo, vt = harness._values(ns_o), harness._values(ns_t)
    shared = sorted(set(vo) & set(vt))
    for name in shared:
        harness._compare_value(vo[name], vt[name], f"value {name}", diffs)
    if out_o != out_t:
        diffs.append("stdout differs")
    verdict["graphs_compared"] = sorted(set(go) & set(gt))
    verdict["values_compared"] = shared
    verdict["names_only_original"] = sorted(set(vo) - set(vt))
    verdict["diffs"] = diffs
    verdict["equivalent"] = not diffs
except Exception:
    import traceback
    verdict["error"] = traceback.format_exc(limit=8)

harness._emit(verdict)
VERDICT = verdict
