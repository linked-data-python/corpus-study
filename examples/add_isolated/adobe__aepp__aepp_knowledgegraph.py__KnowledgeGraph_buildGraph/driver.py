"""Validation driver for
adobe__aepp__aepp_knowledgegraph.py__KnowledgeGraph_buildGraph.

Establishes semantic equivalence of original.py and translated.ldpy.

run_pair's generic entry=/calls= path also compares every argument passed to
the entry point -- fine for RDF terms, wrong here: one argument is a pandas
DataFrame (`==` on two DataFrames is elementwise and its truth value is
ambiguous, so the generic comparator would crash) and another is the `self`
fixture object (two fresh instances per side, compared by identity unless
given __eq__). Both are inputs the region reads, not something whose own
equality is the point. So this driver calls each side directly and compares,
per case, everything the region decides:

  * what the call returns (a graph, by isomorphism, and whether it is the
    graph passed in), or what it raises (type and message);
  * the graph passed in, which the region mutates;
  * `self.global_graph`, which the region sets;
  * the prefix bindings: every binding of the original's graph must be in
    the translation's (`@graph` adds the block's own, record ldpy/027);
  * what it prints (`verbose=True` prints two progress lines);
  * the warnings it emits (recorded, not raised).

Cases, and what each one decides:

  A rich -- the first fixture: two datasets (profile- and identity-enabled),
    three source flows (one loads a dataset, one points at an unknown
    dataset, one has none), two audiences exercising batch / continuous /
    synchronous evaluation and Profile-based / Event-based /
    Relationship-based paths, one destination with primary and mandatory
    attributes and an audience.  The input graph is empty.
  B shared_paths -- the `(node, rdf:type, SCHEMA.path) in graph` branch,
    which A never takes.  The repository reaches it two ways, both here:
      - the input graph already types the path: buildGraph's
        assign_path_schema (aepp/knowledgegraph.py:210-215) writes those
        six triples into the same `graph` before the region runs --
        reproduced for 'web.page.name';
      - two audiences use the same path: aud1 types 'commerce.order.id'
        (else branch), aud3 then finds it typed (if branch).
    Without the branch's island the usedIn triple is missing; with `if
    False:` the else branch adds `SCHEMA.usedIn rdf:nil` as well.  aud1 also
    has two profile paths, so the `Profile-based ... not in graph` guard is
    false the second time (its island is idempotent: a mutant `if True:` is
    equivalent, by construction of the original).  Also: an audience with no
    evaluationInfo, one whose extractPaths returns None (the real method's
    result for an expression format it does not know), a source flow that
    loads a dataset with frequency None, a destination with no attributes, no
    audiences and frequency None (FlowManager reads it with `.get('key')`),
    a dataset with both flags on, one with both off, and NaN rows (a NaN in
    `datalake_rows` makes the column float, as the catalog DataFrame does).
    verbose=False: nothing is printed.
  C only_schema -- `only_schema=True`: the region returns the graph it was
    given, untouched, and prints nothing even with verbose=True.
  D nan_schema -- a dataset whose schemaId is NaN: `URIRef(nan)` raises
    TypeError in the first island.  Both sides must raise the same.  The
    graph is NOT compared here: the original has added two triples before
    raising, the translation's `+{ }` none (it evaluates every term, then
    writes -- record ldpy/014), but in the repository that graph is
    buildGraph's local `graph = Graph()` (aepp/knowledgegraph.py:161),
    dropped with the exception, and `self.global_graph` is not set: the
    partial graph is not observable there.
"""
import contextlib
import io
import json
import sys
import warnings
from pathlib import Path

import pandas as pd
from rdflib import Graph, Literal, URIRef
from rdflib.namespace import RDF, RDFS

from context import FakeFlowManager, FakeKnowledgeGraph
from rdfeval import harness


def _nodes(self):
    return (URIRef(str(self.CATALOG)), URIRef(str(self.PROFILE)),
            URIRef(str(self.FLOWS)), URIRef(str(self.AUDIENCES)))


def _fixture():
    """Case A (the original fixture, unchanged)."""
    self = FakeKnowledgeGraph()
    self.__dataset_preview__ = [
        {"value": "ns1", "fullIDsCount": 42},
        {"value": "ns2", "datasetId": "ds1", "fullIDsCount": 7},
    ]
    self.segmentationAPI._paths_by_audience_id = {
        "aud1": ["web.page.name", "xEvent.commerce.purchases",
                 "_experience.decisioning.propositionEventType@somewhere",
                 "xEvent"],
        "aud2": [],
    }

    df_datasets = pd.DataFrame([
        {"id": "ds1", "schemaId": "https://sandbox/prod/xdm/schema1",
         "name": "Dataset One", "datalake_rows": 100,
         "profileEnabled": True, "identityEnabled": False},
        {"id": "ds2", "schemaId": "https://sandbox/prod/xdm/schema2",
         "name": "Dataset Two", "datalake_rows": 0,
         "profileEnabled": False, "identityEnabled": True},
    ])

    source_flow_managers = [
        FakeFlowManager(id="flow1", name="Ingest One", datasetId="ds1",
                         frequency="batch"),
        FakeFlowManager(id="flow2", name="Ingest Two", datasetId="not-a-dataset",
                         frequency=None),
        FakeFlowManager(id="flow3", name="Ingest Three", datasetId=None),
    ]
    destination_flow_managers = [
        FakeFlowManager(
            id="dest1", name="Destination One", frequency="streaming",
            attributes={
                "web.page.name": {"primary": True, "mandatory": False},
                "commerce.order.id": {"primary": False, "mandatory": True},
            },
            audiences=["aud1"],
        ),
    ]
    audiences = [
        {"id": "aud1", "name": "Audience One",
         "evaluationInfo": {"batch": {"enabled": True},
                             "continuous": {"enabled": False},
                             "synchronous": {"enabled": True}}},
        {"id": "aud2", "name": "Audience Two",
         "evaluationInfo": {"batch": {"enabled": False},
                             "continuous": {"enabled": True},
                             "synchronous": {"enabled": False}}},
    ]

    CATALOG_NODE, PROFILE_NODE, FLOWS_NODE, AUDIENCES_NODE = _nodes(self)

    return (self, {"only_schema": False, "verbose": True}, df_datasets,
            Graph(), CATALOG_NODE, PROFILE_NODE, FLOWS_NODE, AUDIENCES_NODE,
            source_flow_managers, audiences, destination_flow_managers)


def _schema_paths(self, graph, schema_id, paths):
    """What assign_path_schema (aepp/knowledgegraph.py:210-215) writes into
    `graph` before the region runs, for each observable-schema path."""
    sch = URIRef(schema_id)
    for path, title, xdm_type in paths:
        node = self.SCHEMA[path.replace('{}', '').replace('[]', '')]
        graph.add((sch, self.SCHEMA.contains, node))
        graph.add((node, self.SCHEMA.usedIn, sch))
        graph.add((node, RDFS.label, Literal(title)))
        graph.add((node, RDF.type, self.SCHEMA.path))
        graph.add((node, self.SCHEMA.xdmType, Literal(xdm_type)))
        graph.add((node, self.CATALOG.hasData, Literal(True)))


def _shared_paths():
    """Case B: the already-typed path branch, and the secondary branches."""
    self = FakeKnowledgeGraph()
    self.__dataset_preview__ = [
        {"value": "ds3", "datasetId": "ds3", "fullIDsCount": 3},
    ]
    self.segmentationAPI._paths_by_audience_id = {
        "aud1": ["web.page.name", "commerce.order.id"],
        "aud3": ["commerce.order.id", "xEvent.web.webPageDetails.name",
                 "xEvent"],
        "aud4": None,
    }
    graph = Graph()
    _schema_paths(self, graph, "https://sandbox/prod/xdm/schema3",
                  [("web.page.name", "Page name", "string")])

    df_datasets = pd.DataFrame([
        {"id": "ds3", "schemaId": "https://sandbox/prod/xdm/schema3",
         "name": "Dataset Three", "datalake_rows": 12,
         "profileEnabled": True, "identityEnabled": True},
        {"id": "ds4", "schemaId": "https://sandbox/prod/xdm/schema4",
         "name": float("nan"), "datalake_rows": float("nan"),
         "profileEnabled": False, "identityEnabled": False},
    ])
    source_flow_managers = [
        FakeFlowManager(id="flow4", name="Ingest Four", datasetId="ds3",
                         frequency=None),
    ]
    destination_flow_managers = [
        FakeFlowManager(id="dest2", name="Destination Two", frequency=None),
    ]
    audiences = [
        {"id": "aud1", "name": "Audience One"},
        {"id": "aud3", "name": "Audience Three",
         "evaluationInfo": {"continuous": {"enabled": True}}},
        {"id": "aud4", "name": "Audience Four",
         "evaluationInfo": {"batch": {"enabled": True}}},
    ]
    return (self, {"only_schema": False, "verbose": False}, df_datasets,
            graph, *_nodes(self), source_flow_managers, audiences,
            destination_flow_managers)


def _only_schema():
    """Case C: only_schema=True returns the graph untouched, prints nothing."""
    args = list(_fixture())
    self = args[0]
    graph = Graph()
    _schema_paths(self, graph, "https://sandbox/prod/xdm/schema1",
                  [("web.page.name", "Page name", "string")])
    args[1] = {"only_schema": True, "verbose": True}
    args[3] = graph
    return tuple(args)


def _nan_schema():
    """Case D: URIRef(nan) raises in the first island."""
    args = list(_fixture())
    args[2] = pd.DataFrame([
        {"id": "ds5", "schemaId": float("nan"), "name": "Dataset Five",
         "datalake_rows": 1, "profileEnabled": True,
         "identityEnabled": False},
    ])
    return tuple(args)


CASES = [
    ("A rich", _fixture, True),
    ("B shared_paths", _shared_paths, True),
    ("C only_schema", _only_schema, True),
    ("D nan_schema", _nan_schema, False),
]


def _run(fn, args):
    out = io.StringIO()
    with contextlib.redirect_stdout(out), \
            warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        try:
            result, raised = fn(*args), None
        except Exception as e:                    # noqa: BLE001 - compared
            result, raised = None, (type(e).__name__, str(e))
    return {"result": result, "raised": raised, "stdout": out.getvalue(),
            "warnings": [(w.category.__name__, str(w.message))
                         for w in caught],
            "self": args[0], "graph": args[3]}


def _iso(a, b):
    if a is None or b is None:
        return a is b
    return harness.graphs_isomorphic(a, b)


def _compare(label, o, t, compare_graph, diffs):
    if o["raised"] != t["raised"]:
        diffs.append(f"{label}: outcome differs ({o['raised']} vs {t['raised']})")
    if o["stdout"] != t["stdout"]:
        diffs.append(f"{label}: stdout differs ({o['stdout']!r} vs {t['stdout']!r})")
    if o["warnings"] != t["warnings"]:
        diffs.append(f"{label}: warnings differ ({o['warnings']} vs {t['warnings']})")
    if not compare_graph:
        return
    if not _iso(o["result"], t["result"]):
        diffs.append(f"{label}: result graphs not isomorphic")
    if (o["result"] is o["graph"]) != (t["result"] is t["graph"]):
        diffs.append(f"{label}: result is / is not the graph passed in")
    if not _iso(o["graph"], t["graph"]):
        diffs.append(f"{label}: input graphs not isomorphic "
                     f"({len(o['graph'])} vs {len(t['graph'])} triples)")
    if not _iso(o["self"].global_graph, t["self"].global_graph):
        diffs.append(f"{label}: self.global_graph differs")
    missing = set(o["graph"].namespaces()) - set(t["graph"].namespaces())
    if missing:
        diffs.append(f"{label}: prefix bindings lost {sorted(missing)}")


ex_dir = Path(__file__).resolve().parent
verdict: dict = {"example": ex_dir.name, "equivalent": False,
                 "method": "entry:build_graph_region (custom: isomorphism, "
                           "stdout, warnings, raises, attributes)",
                 "diffs": [], "error": None}
try:
    ns_o, out_o = harness._exec_python(ex_dir / "original.py")
    ns_t, out_t = harness._exec_ldpy(ex_dir / "translated.ldpy")
    diffs = []
    if out_o != out_t:
        diffs.append("stdout differs at module level")
    for label, make, compare_graph in CASES:
        o = _run(ns_o["build_graph_region"], make())
        t = _run(ns_t["build_graph_region"], make())
        _compare(label, o, t, compare_graph, diffs)
    verdict["calls"] = len(CASES)
    verdict["diffs"] = diffs
    verdict["equivalent"] = not diffs
except Exception:
    import traceback
    verdict["error"] = traceback.format_exc(limit=8)

harness._emit(verdict)   # credits the sides it executed (RDFEVAL_SIDES)
VERDICT = verdict
