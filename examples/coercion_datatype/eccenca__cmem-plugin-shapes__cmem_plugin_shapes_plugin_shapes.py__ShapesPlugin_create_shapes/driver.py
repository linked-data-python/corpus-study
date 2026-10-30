"""Validation driver for
eccenca__cmem-plugin-shapes__cmem_plugin_shapes_plugin_shapes.py__ShapesPlugin_create_shapes.

`create_shapes` is a method (`self` an explicit first parameter).  Both sides
carry an identical `demo(class_dict)` harness (see meta.json and original.py)
that builds a SimpleNamespace `self` and returns `self.shapes_graph`; the first
two calls below (CALL_1, CALL_2) are the original ones and go through it.

`demo` observes only the final graph of a run that never fails.  What the
real plugin relies on is more than that, so the other scenarios build `self`
here, call each side's `create_shapes(self)` directly, and compare four
things per scenario:

  * the exception, if any (type and message): `get_name` is a network call
    (plugin_shapes.py:299-311) that raises on `raise_for_status()`, on a
    malformed IRI (ValueError) or on a missing "title";
  * the shapes graph AFTER the call, whether it raised or not: the original
    has already added the earlier triples of a node shape when `get_name`
    raises, and an island that moves the call ahead of them changes what is
    left in the graph;
  * `shapes_count`, which feeds `entity_count` of the execution report
    (plugin_shapes.py:670) and is incremented once per new shape;
  * the list of IRIs passed to `get_name`, in order (one call per new node
    shape and per new property shape, none for a deduplicated one).

`self` has the attributes the real plugin sets: `shapes_graph` starts as the
catalogue graph `init_shapes_graph()` builds (a ShapeCatalog type and a
dcterms:source triple), `shapes_count` starts at 0, and the class dict has the
shape `get_class_dict()` builds: IRIs as `str`, `data` and `inverse` real
`bool`s (`str2bool`), a property listed once per distinct (property, data,
inverse) tuple.

Scenarios (each is a driver case, see SCENARIOS):

  main        two classes, a property shared between them (dedup guard hit
              across classes), an inverse one (SHUI.inversePath, "← "
              prefix on the name), both nodeKind branches.
  same-prop   the same property listed twice in one class with data True then
              False (what DISTINCT ?data gives for a property used with
              literals and IRIs): same uuid, so the second entry only adds the
              sh:property link -- shapes_count and get_name calls show it.
  both-dir    a property in both directions: two uuids, two shapes; its
              name is empty, so the arrow alone is the inverse shape's label.
  iri-forms-hash, iri-forms-slash  shapes_graph_iri ending in "#" and in "/"
              (the default one, in the other scenarios, ends in neither and
              gets a "/" from format_namespace).
  empty-and-odd-names  an empty class name, and property names with a quote,
              a newline, a backslash and a non-ASCII letter (name coercion,
              `{name}@en` against Literal(name, lang="en")).
  distinct-names  one property only, the name for the class and for the
              property differ, so sh:name of a node cannot be taken for the
              property's.
  get_name-raises-node      get_name raises for the second class (the first
              one is complete): the original keeps the node shape's `a
              sh:NodeShape` and `sh:targetClass` triples.
  get_name-raises-property  get_name raises for the second property of the
              first class: the first property's shape is complete and linked,
              the second one has written nothing yet (get_name comes before
              its first add) but shapes_count has moved.
  get_name-raises-first-node  get_name raises for the very first class.
  empty       an empty class dict.
  no-props    a class with an empty property list: only the node shape.

The class-level dedup guard (`class_uuid not in class_uuids`) cannot be
reached: `get_class_dict` returns a dict, whose keys are distinct IRIs and so
distinct uuid5 values.  The scenarios do not try to make it false.
"""
import copy
import json
import sys
from pathlib import Path
from types import SimpleNamespace

from rdflib import DCTERMS, RDF, Graph, URIRef

from rdfeval import harness
from rdfeval.harness import run_pair  # noqa: F401  (documented entry for demo calls)

SHUI = "https://vocab.eccenca.com/shui/"
P = "http://example.org/data#"


def prop(name, data=False, inverse=False):
    return {"property": P + name, "data": data, "inverse": inverse}


def named(iri):
    return iri.rsplit("#", 1)[-1].rsplit("/", 1)[-1]


# CALL_1 / CALL_2: the original two calls, through demo(class_dict)
CALL_1 = {
    P + "Person": [prop("name", data=True), prop("knows", inverse=True)],
    P + "Organization": [prop("name", data=True)],
}
CALL_2 = {}

SCENARIOS = [
    dict(label="main", classes=CALL_1),
    dict(label="same-prop", classes={
        P + "Person": [prop("homepage", data=True), prop("homepage", data=False)],
        P + "Document": [prop("homepage", data=False)],
    }),
    dict(label="both-dir", classes={
        P + "Person": [prop("knows", inverse=False), prop("knows", inverse=True)],
    }, names={P + "knows": ""}),
    dict(label="iri-forms-hash", classes={P + "A": [prop("p", data=True)]},
         iri="https://example.org/shapes#"),
    dict(label="iri-forms-slash", classes={P + "A": [prop("p", data=True)]},
         iri="https://example.org/shapes/"),
    dict(label="empty-and-odd-names", classes={
        P + "Empty": [prop("q", data=True, inverse=True)],
        P + "Odd": [prop("r", data=False)],
    }, names={P + "Empty": "", P + "q": "a \"q\"\n\\ ü", P + "Odd": "café (ex)"}),
    dict(label="distinct-names", classes={P + "Thing": [prop("label")]},
         names={P + "Thing": "The Thing", P + "label": "the label"}),
    dict(label="get_name-raises-node", classes={
        P + "Person": [prop("name", data=True)],
        P + "Organization": [prop("name", data=True)],
    }, fail={P + "Organization": ValueError("Invalid class or property (Organization).")}),
    dict(label="get_name-raises-property", classes={
        P + "Person": [prop("name", data=True), prop("knows"), prop("age", data=True)],
    }, fail={P + "knows": RuntimeError("500 Server Error")}),
    dict(label="get_name-raises-first-node", classes=CALL_1,
         fail={P + "Person": ValueError("Invalid class or property (Person).")}),
    dict(label="empty", classes={}),
    dict(label="no-props", classes={P + "Lonely": [], P + "Other": [prop("x")]}),
]


def make_self(sc, log):
    iri = sc.get("iri", "https://example.org/shapes")
    names = sc.get("names", {})
    fail = sc.get("fail", {})
    graph = Graph()
    graph.add((URIRef(iri), RDF.type, URIRef(SHUI + "ShapeCatalog")))
    graph.add((URIRef(iri), DCTERMS.source, URIRef("http://example.org/data")))

    def get_name(i):
        log.append(i)
        if i in fail:
            raise fail[i]
        return names.get(i, named(i))

    return SimpleNamespace(
        shapes_graph=graph,
        shapes_graph_iri=iri,
        shapes_count=0,
        get_class_dict=lambda: copy.deepcopy(sc["classes"]),
        get_name=get_name,
    )


def outcome(ns, sc):
    log: list = []
    me = make_self(sc, log)
    raised = None
    try:
        ns["create_shapes"](me)
    except Exception as e:  # noqa: BLE001 - compared
        raised = f"{type(e).__name__}: {e}"
    return me.shapes_graph, {"raised": raised, "shapes_count": me.shapes_count,
                             "get_name_calls": log}


ex_dir = Path(__file__).resolve().parent
verdict: dict = {"example": ex_dir.name, "equivalent": False,
                 "method": "demo calls + create_shapes(self) per scenario "
                           "(graph, exception, shapes_count, get_name calls)",
                 "diffs": [], "error": None}
try:
    ns_o, _ = harness._exec_python(ex_dir / "original.py")
    ns_t, _ = harness._exec_ldpy(ex_dir / "translated.ldpy")
    diffs: list = []
    for i, cd in enumerate((CALL_1, CALL_2)):
        go, gt = ns_o["demo"](copy.deepcopy(cd)), ns_t["demo"](copy.deepcopy(cd))
        if not harness.graphs_isomorphic(go, gt):
            diffs.append(f"demo call {i + 1}: graphs not isomorphic ({len(go)} vs {len(gt)} triples)")
    for sc in SCENARIOS:
        go, so = outcome(ns_o, sc)
        gt, st = outcome(ns_t, sc)
        if not harness.graphs_isomorphic(go, gt):
            diffs.append(f"{sc['label']}: graphs not isomorphic ({len(go)} vs {len(gt)} triples)")
        for key in so:
            if so[key] != st[key]:
                diffs.append(f"{sc['label']}.{key}: {so[key]!r} vs {st[key]!r}")
    verdict["diffs"] = diffs
    verdict["equivalent"] = not diffs
    verdict["scenarios"] = len(SCENARIOS)
except Exception:
    import traceback
    verdict["error"] = traceback.format_exc(limit=8)

harness._emit(verdict)
VERDICT = verdict
