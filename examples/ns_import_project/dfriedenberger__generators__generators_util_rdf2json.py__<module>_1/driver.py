"""Validation driver for dfriedenberger__generators__generators_util_rdf2json.py__<module>_1.

This region READS a graph -- it walks key/value-pair structures rooted at an
anchor subject and returns a JSON-shaped Python value (dict/list/str/int/
float/bool) -- so the oracle is not isomorphism but equality of the values
both versions produce from the same input graph (corpus/405, INSTRUCTIONS_403
§3). meta.json's oracle was corrected from the mechanical draft's
"isomorphism" to "values" accordingly.

fixture.ttl anchors two subjects:

  * ex:obj1 carries one key/value pair of every shape process_value handles:
    a plain (undatatyped) literal, xsd:integer, xsd:float, xsd:boolean, an
    rdf:Seq list of two literals (exercises process_seq's rdf:_1/rdf:_2
    walk), and a nested ans:Dictionary with its own key/value pair
    (exercises the recursion back into process_key_value_pairs).
  * ex:obj2 has no ans:hasKeyValuePair triple at all -- the zero-solutions
    case: process_key_value_pairs must return {} on both sides, not raise.

A kv-pair node reachable from nothing (ex:kv-orphan) and a differently-named
predicate pointing at a real kv-pair node (ex:obj3 ex:notHasKeyValuePair
ex:kv-name) are the neighbourhood that must not leak into either result.

Custom driver, not the generic run_pair(entry=..., calls=...) path: the
region's own signature takes a SparQLWrapper instance, not a bare Graph, and
run_pair's generic per-argument comparison (meant to catch mutation of a
Graph argument, isomorphism-compared) falls back to identity equality for a
plain object it does not special-case -- SparQLWrapper has no __eq__ (kept
verbatim from obse, see generators_context.py), so two separately
constructed instances always compare unequal even when their wrapped graphs
are isomorphic and the function never mutates them. That is a false
difference in the ARGUMENT, not in the region's actual output. This driver
sidesteps it by comparing only what the region actually produces: the
returned JSON-shaped value, built fresh per side from `ns_o`/`ns_t`'s own
bound SparQLWrapper class (the same one process_key_value_pairs receives).

`tags` is a real ordered sequence (process_seq walks rdf:_1, rdf:_2, ... by
explicit index, not by store iteration order), so results are compared
`ordered=True` -- this region DOES impose an order on that one list.
"""
import traceback
from pathlib import Path

from rdflib import Namespace

from rdfeval.harness import _compare_value, _emit, _exec_ldpy, _exec_python, fixture_graph

FIXTURE = Path(__file__).resolve().parent / "fixture.ttl"
EX = Namespace("http://example.org/data/")
ANCHORS = ["obj1", "obj2"]


def main() -> dict:
    ex_dir = Path(__file__).resolve().parent
    verdict: dict = {"example": ex_dir.name, "equivalent": False,
                     "method": "custom:fixture-values", "diffs": [], "error": None}
    try:
        ns_o, out_o = _exec_python(ex_dir / "original.py")
        ns_t, out_t = _exec_ldpy(ex_dir / "translated.ldpy")
    except Exception:
        verdict["error"] = traceback.format_exc(limit=8)
        _emit(verdict)
        return verdict

    fo, ft = ns_o.get("process_key_value_pairs"), ns_t.get("process_key_value_pairs")
    wrap_o, wrap_t = ns_o.get("SparQLWrapper"), ns_t.get("SparQLWrapper")
    if not callable(fo) or not callable(ft):
        verdict["error"] = "process_key_value_pairs not found in both modules"
        _emit(verdict)
        return verdict

    diffs: list[str] = []
    for anchor in ANCHORS:
        try:
            ro = fo(wrap_o(fixture_graph(FIXTURE)), EX[anchor])
            rt = ft(wrap_t(fixture_graph(FIXTURE)), EX[anchor])
        except Exception:
            verdict["error"] = traceback.format_exc(limit=8)
            _emit(verdict)
            return verdict
        _compare_value(ro, rt, f"{anchor}.result", diffs, ordered=True)

    if out_o != out_t:
        diffs.append("stdout differs")

    verdict["diffs"] = diffs
    verdict["equivalent"] = not diffs
    _emit(verdict)
    return verdict


VERDICT = main()
