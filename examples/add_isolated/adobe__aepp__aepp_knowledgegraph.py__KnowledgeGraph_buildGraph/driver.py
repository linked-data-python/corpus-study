"""Validation driver for
adobe__aepp__aepp_knowledgegraph.py__KnowledgeGraph_buildGraph.

Establishes semantic equivalence of original.py and translated.ldpy.

run_pair's generic entry=/calls= path also compares every argument passed to
the entry point -- fine for RDF terms, wrong here: one argument is a pandas
DataFrame (`==` on two DataFrames is elementwise and its truth value is
ambiguous, so the generic comparator would crash) and another is the `self`
fixture object (two fresh instances per side, compared by identity unless
given __eq__). Both are inputs the region reads, not something whose own
equality is the point. So this driver calls each side directly and compares
only what the region is supposed to produce: the returned graph.
"""
import json
import sys
from pathlib import Path

import pandas as pd
from rdflib import Graph, URIRef

from context import FakeFlowManager, FakeKnowledgeGraph
from rdfeval import harness


def _fixture():
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

    CATALOG_NODE = URIRef(str(self.CATALOG))
    PROFILE_NODE = URIRef(str(self.PROFILE))
    FLOWS_NODE = URIRef(str(self.FLOWS))
    AUDIENCES_NODE = URIRef(str(self.AUDIENCES))

    return (self, {"only_schema": False, "verbose": True}, df_datasets,
            Graph(), CATALOG_NODE, PROFILE_NODE, FLOWS_NODE, AUDIENCES_NODE,
            source_flow_managers, audiences, destination_flow_managers)


ex_dir = Path(__file__).resolve().parent
verdict: dict = {"example": ex_dir.name, "equivalent": False,
                 "method": "entry:build_graph_region (custom: isomorphism only)",
                 "diffs": [], "error": None}
try:
    ns_o, out_o = harness._exec_python(ex_dir / "original.py")
    ns_t, out_t = harness._exec_ldpy(ex_dir / "translated.ldpy")
    g_o = ns_o["build_graph_region"](*_fixture())
    g_t = ns_t["build_graph_region"](*_fixture())
    diffs = []
    if not harness.graphs_isomorphic(g_o, g_t):
        diffs.append(f"result graphs not isomorphic ({len(g_o)} vs {len(g_t)} triples)")
    verdict["diffs"] = diffs
    verdict["equivalent"] = not diffs
except Exception:
    import traceback
    verdict["error"] = traceback.format_exc(limit=8)

print("RDFEVAL-VERDICT " + json.dumps(verdict), file=sys.stderr)
VERDICT = verdict
