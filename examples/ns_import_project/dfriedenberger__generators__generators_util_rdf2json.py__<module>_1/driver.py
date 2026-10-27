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

REPAIR PASS (AGENT_REPAIR.md).  The first version of this driver let three
mutants through, on all three artefacts: int(literal) -> float(literal)
(because 42 == 42.0), each `raise ValueError(...)` -> `return None` (because
no case raised), and the removal of the "has_<key>" length guard (because no
list was empty).  It now:

  * compares VALUES BY TYPE, not by ==.  `typed()` turns a result into
    (type name, repr) leaves, so int 1, float 1.0 and bool True are three
    different values, and a dict keeps its order-free equality;
  * compares OUTCOMES, not just values.  `outcome()` records either
    ("returns", typed result) or ("raises", exception class, message), so a
    side that raises where the other returns None -- or raises a different
    ValueError -- is a difference.  Without it the driver itself would crash
    on the first raise and say nothing;
  * drives the fixture's new anchors: ex:obj-types (one pair per datatype
    shape: xsd:integer, xsd:float incl. a whole float, NaN and INF,
    xsd:boolean "true"/"false"/"0"/"1", and four undatatyped strings, among
    them "" and "42"), ex:obj-lists (empty rdf:Seq -> [] without "has_",
    typed members, twelve members read by number, a gap that ends the walk, a
    list holding a list and a dictionary, a node both rdf:Seq and
    ans:Dictionary, an empty dictionary) and the eleven ex:err-* anchors, each
    of which must raise ValueError (xsd:string, xsd:date, xsd:double,
    xsd:decimal, a bare IRI, a bare blank node, ill-typed xsd:integer /
    xsd:float lexical forms, and the same errors from inside a dictionary and
    a list);
  * also calls the three inner functions directly: process_value on every
    value node of the fixture and of fixture_missing.ttl (so the final
    `raise ValueError` is reached with a URIRef, a BNode, a Literal-less
    None), process_seq on every rdf:Seq node and on a node that is not a list,
    and literal_to_value on python-built literals (Literal(42), Literal(True),
    Literal(1.5), Literal("x", datatype=XSD.string), ...);
  * reads a second graph, fixture_missing.ttl, that has no rdf:Seq at all: in
    fixture.ttl `(None, rdf:type, rdf:Seq) in graph` is a wildcard match, so a
    pair without ans:value would be read as a list there.  The missing-value
    and missing-key pairs go through that graph.

`tags` is a real ordered sequence (process_seq walks rdf:_1, rdf:_2, ... by
explicit index, not by store iteration order), so results are compared
`ordered=True` -- this region DOES impose an order on that one list.
"""
import logging
import traceback
from pathlib import Path

from rdflib import BNode, Literal, Namespace, URIRef
from rdflib.namespace import XSD

from rdfeval.harness import _compare_value, _emit, _exec_ldpy, _exec_python, fixture_graph

FIXTURE = Path(__file__).resolve().parent / "fixture.ttl"
FIXTURE_MISSING = Path(__file__).resolve().parent / "fixture_missing.ttl"
EX = Namespace("http://example.org/data/")
ANS = Namespace("http://example.org/dfriedenberger/generators/assets#")
# rdflib logs a traceback for each ill-typed literal it parses ("abc"^^xsd:integer);
# those are deliberate fixture cases, so keep the log quiet.
logging.getLogger("rdflib.term").setLevel(logging.CRITICAL)
RDF_SEQ = URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#Seq")

# anchors that must RETURN a dict through process_key_value_pairs
ANCHORS = ["obj1", "obj2", "obj-types", "obj-lists"]
# anchors that must RAISE ValueError through process_key_value_pairs
ERROR_ANCHORS = ["err-string", "err-date", "err-double", "err-decimal",
                 "err-iri", "err-bnode", "err-int-lex", "err-int-dec",
                 "err-float-lex", "err-deep-dict", "err-deep-list",
                 "err-deep-iri"]
# anchors of fixture_missing.ttl: a pair with no value, no key, neither
MISSING_ANCHORS = ["no-value", "no-key", "no-either"]
# literals built in Python, handed straight to literal_to_value
LITERALS = [Literal(42), Literal(-3), Literal(1.5), Literal(True), Literal(False),
            Literal("x"), Literal(""), Literal("x", lang="en"),
            Literal("1", datatype=XSD.integer), Literal("1", datatype=XSD.float),
            Literal("1", datatype=XSD.boolean), Literal("0", datatype=XSD.boolean),
            Literal("x", datatype=XSD.string), Literal("1", datatype=XSD.double),
            Literal("1", datatype=XSD.decimal), Literal("2020-01-01", datatype=XSD.date)]


def typed(value):
    """A result made comparable BY TYPE: 1, 1.0 and True stay three values."""
    if isinstance(value, dict):
        return {f"{type(k).__name__}:{k!r}": typed(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [type(value).__name__, [typed(v) for v in value]]
    return (type(value).__name__, repr(value))


def outcome(call):
    """What a call does: its typed result, or the exception it raises."""
    try:
        return ["returns", typed(call())]
    except Exception as e:  # noqa: BLE001 -- the exception IS the observation
        return ["raises", type(e).__name__, str(e)]


def side_cases(ns: dict) -> dict:
    """Every observation of one side, by label; each builds its own graph."""
    wrap = ns["SparQLWrapper"]
    kv, pv, ps, lv = (ns["process_key_value_pairs"], ns["process_value"],
                      ns["process_seq"], ns["literal_to_value"])
    cases: dict = {}

    def graph_of(path):
        return wrap(fixture_graph(path))

    for anchor in ANCHORS + ERROR_ANCHORS:
        cases[f"kv {anchor}"] = outcome(lambda: kv(graph_of(FIXTURE), EX[anchor]))
    for anchor in MISSING_ANCHORS:
        cases[f"kv {anchor} (missing graph)"] = outcome(
            lambda: kv(graph_of(FIXTURE_MISSING), EX[anchor]))

    # process_value on every value node of the fixtures, and on non-nodes
    for path in (FIXTURE, FIXTURE_MISSING):
        values = sorted(set(fixture_graph(path).objects(None, ANS.value)), key=repr)
        for node in values:
            if isinstance(node, BNode):
                continue  # a fresh bnode per side: reached through kv err-bnode
            cases[f"process_value {path.name} {node!r}"] = outcome(
                lambda: pv(graph_of(path), node))
    cases["process_value None (missing graph)"] = outcome(
        lambda: pv(graph_of(FIXTURE_MISSING), None))
    cases["process_value bare IRI (missing graph)"] = outcome(
        lambda: pv(graph_of(FIXTURE_MISSING), EX["untyped-node"]))
    cases["process_value bare BNode (missing graph)"] = outcome(
        lambda: pv(graph_of(FIXTURE_MISSING), BNode()))
    cases["process_value plain literal (missing graph)"] = outcome(
        lambda: pv(graph_of(FIXTURE_MISSING), Literal("x")))

    # process_seq on every rdf:Seq node, and on a node that is not a list
    for seq in sorted(fixture_graph(FIXTURE).subjects(None, RDF_SEQ), key=repr):
        cases[f"process_seq {seq!r}"] = outcome(lambda: ps(graph_of(FIXTURE), seq))
    cases["process_seq on a non-list"] = outcome(
        lambda: ps(graph_of(FIXTURE), EX["obj2"]))

    for i, lit in enumerate(LITERALS):
        cases[f"literal_to_value #{i} {lit!r}"] = outcome(lambda: lv(lit))
    return cases


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

    for name in ("process_key_value_pairs", "process_value", "process_seq",
                 "literal_to_value", "SparQLWrapper"):
        if not callable(ns_o.get(name)) or not callable(ns_t.get(name)):
            verdict["error"] = f"{name} not found in both modules"
            _emit(verdict)
            return verdict

    try:
        cases_o, cases_t = side_cases(ns_o), side_cases(ns_t)
    except Exception:
        verdict["error"] = traceback.format_exc(limit=8)
        _emit(verdict)
        return verdict

    diffs: list[str] = []
    if cases_o.keys() != cases_t.keys():
        diffs.append("the two sides observed different cases")
    for label in cases_o:
        _compare_value(cases_o[label], cases_t.get(label), label, diffs, ordered=True)
    # the driver must really exercise the error branches, not skip them
    raised = [k for k, v in cases_o.items() if v[0] == "raises"]
    if len(raised) < len(ERROR_ANCHORS):
        diffs.append(f"driver exercised only {len(raised)} raising cases")
    verdict["cases"] = len(cases_o)
    verdict["raising_cases"] = len(raised)

    if out_o != out_t:
        diffs.append("stdout differs")

    verdict["diffs"] = diffs
    verdict["equivalent"] = not diffs
    _emit(verdict)
    return verdict


VERDICT = main()
