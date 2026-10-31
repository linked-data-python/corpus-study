"""Validation driver for OntoUML__ontouml-json2graph__json2graph_decoder_decode_obj_property.py__set_cardinality_relations.

Establishes semantic equivalence of original.py and translated.ldpy.

set_cardinality_relations(property_dict, ontouml_graph) returns None and
mutates ontouml_graph in place.  run_pair compares that graph by isomorphism
only; the region also decides things it does not see, so this driver calls
each side itself and compares, per case:

  * what the call raises (type and message) -- the 'error' policy raises
    before any triple is written, on both sides;
  * the graph passed in, by isomorphism;
  * its prefix bindings: every binding of the original's graph must still be
    in the translation's (`@graph ontouml_graph` binds the block's `xsd:`;
    extra bindings are tolerated, record ldpy/027).  The repository's graph
    is built with `bind("ontouml", ...)` and `bind("", base_uri)`
    (decoder/decode_main.py:131-133) and serialised
    (modules/input_output.py:81), so cases D-K pass a graph shaped like it;
  * the warnings emitted (category and message), recorded, not raised:
    resolve_cardinality warns on every invalid or repaired value;
  * what it prints.

The invalid-cardinality policy is a context line, not an argument: it is
read from `modules.arguments.ARGUMENTS`, the same shim module object on both
sides.  Each case sets it before each side's call and the driver restores
"preserve" at the end.

Cases, and what each one decides:

  A-C  the three original calls, unchanged: a range "0..3" (typed
       lowerBound), "*" (lower "0", upper "*"), and an unparsable value
       under 'preserve' (no lowerBound/upperBound triples).
  D    no "cardinality" key: the outer guard is false and nothing is
       written.  Real: decode_main.py:137 runs clean_null_data, which drops
       a `"cardinality": null` (tests/test_files/test_027.json:80), so a
       Property reaches the region without the key.  Kills an outer guard
       forced to True (KeyError).
  E    exact "1": lower = upper = "1", cardinalityValue repaired to "1..1".
  F    "0..0": lower "0" -- a falsy-looking str, still emitted.
  G    "" under 'preserve': cardinalityValue "" (an empty plain literal),
       no bounds, a warning.
  H    "1,,*" under 'repair': repaired to "1..*", bounds emitted, a
       CardinalityRepairWarning.
  I    "x..y" under 'repair': unrepairable, no bounds, a warning.
  J    "x..y" under 'error': InvalidCardinalityError, graph untouched.
  K    "2..1" under 'preserve': lower > upper is invalid, no bounds.

Every value reaching a term is a str (a JSON string, or a regex group of
one) or None; None is never written (the guard).  The coercions agree for
every such value: `{full_cardinality}` / `{upper_bound}` go through
ldpy's node(), equal to Literal(str); `{lower_bound}^^xsd:...` transpiles to
the very Literal(lower_bound, datatype=...) call of the original.
"""
import contextlib
import io
import warnings
from pathlib import Path

from rdflib import Graph

from rdfeval import harness


def caller_graph():
    """The graph decode_main.py:131-133 builds before decoding."""
    g = Graph()
    g.bind("ontouml", "https://w3id.org/ontouml#")
    g.bind("", "https://example.org#")
    return g


CASES = [
    # (label, property_dict, graph factory, invalid_cardinality_policy)
    ("A range", {"cardinality": "0..3", "id": "prop-range"}, Graph, "preserve"),
    ("B star", {"cardinality": "*", "id": "prop-star"}, Graph, "preserve"),
    ("C invalid", {"cardinality": "not-a-cardinality", "id": "prop-invalid"},
     Graph, "preserve"),
    ("D no key", {"id": "prop-nokey", "name": "p"}, caller_graph, "preserve"),
    ("E exact", {"cardinality": "1", "id": "prop-exact"}, caller_graph,
     "preserve"),
    ("F zero", {"cardinality": "0..0", "id": "prop-zero"}, caller_graph,
     "preserve"),
    ("G empty", {"cardinality": "", "id": "prop-empty"}, caller_graph,
     "preserve"),
    ("H repaired", {"cardinality": "1,,*", "id": "prop-repair"},
     caller_graph, "repair"),
    ("I unrepairable", {"cardinality": "x..y", "id": "prop-norepair"},
     caller_graph, "repair"),
    ("J error", {"cardinality": "x..y", "id": "prop-error"}, caller_graph,
     "error"),
    ("K reversed", {"cardinality": "2..1", "id": "prop-reversed"},
     caller_graph, "preserve"),
]


def _run(fn, property_dict, graph, policy):
    import modules.arguments as args
    args.ARGUMENTS["invalid_cardinality_policy"] = policy
    out = io.StringIO()
    with contextlib.redirect_stdout(out), \
            warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        try:
            result, raised = fn(dict(property_dict), graph), None
        except Exception as e:                    # noqa: BLE001 - compared
            result, raised = None, (type(e).__name__, str(e))
    return {"result": result, "raised": raised, "stdout": out.getvalue(),
            "warnings": [(w.category.__name__, str(w.message))
                         for w in caught],
            "graph": graph}


def _compare(label, o, t, diffs):
    if o["raised"] != t["raised"]:
        diffs.append(f"{label}: outcome differs ({o['raised']} vs {t['raised']})")
    if o["result"] != t["result"]:
        diffs.append(f"{label}: result differs ({o['result']!r} vs {t['result']!r})")
    if o["stdout"] != t["stdout"]:
        diffs.append(f"{label}: stdout differs")
    if o["warnings"] != t["warnings"]:
        diffs.append(f"{label}: warnings differ ({o['warnings']} vs {t['warnings']})")
    if not harness.graphs_isomorphic(o["graph"], t["graph"]):
        diffs.append(f"{label}: graphs not isomorphic "
                     f"({len(o['graph'])} vs {len(t['graph'])} triples)")
    lost = set(o["graph"].namespaces()) - set(t["graph"].namespaces())
    if lost:
        diffs.append(f"{label}: prefix bindings lost {sorted(lost)}")


ex_dir = Path(__file__).resolve().parent
verdict: dict = {"example": ex_dir.name, "equivalent": False,
                 "method": "entry:set_cardinality_relations (custom: "
                           "isomorphism, bindings, warnings, raises, stdout)",
                 "diffs": [], "error": None}
try:
    ns_o, out_o = harness._exec_python(ex_dir / "original.py")
    ns_t, out_t = harness._exec_ldpy(ex_dir / "translated.ldpy")
    diffs: list[str] = []
    if out_o != out_t:
        diffs.append("stdout differs at module level")
    fo, ft = ns_o["set_cardinality_relations"], ns_t["set_cardinality_relations"]
    for label, pdict, make_graph, policy in CASES:
        o = _run(fo, pdict, make_graph(), policy)
        t = _run(ft, pdict, make_graph(), policy)
        _compare(label, o, t, diffs)
    import modules.arguments as args
    args.ARGUMENTS["invalid_cardinality_policy"] = "preserve"
    verdict["calls"] = len(CASES)
    verdict["diffs"] = diffs
    verdict["equivalent"] = not diffs
except Exception:
    import traceback
    verdict["error"] = traceback.format_exc(limit=8)

harness._emit(verdict)
VERDICT = verdict
