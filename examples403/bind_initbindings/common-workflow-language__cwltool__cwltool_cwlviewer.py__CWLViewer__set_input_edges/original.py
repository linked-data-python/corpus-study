# Extracted from common-workflow-language/cwltool@9f6fcba256 : cwltool/cwlviewer.py
# region: CWLViewer._set_input_edges (lines 113-142, stratum bind_initbindings)
# licence of the source repository: see meta.json
from collections.abc import Iterator
from typing import cast
from urllib.parse import urlparse
import pydot
import rdflib

def _set_input_edges(self) -> None:
    get_input_edges_query = _get_input_edges_query()
    inputs_subgraph = pydot.Subgraph(graph_name="cluster_inputs")
    self._dot_graph.add_subgraph(inputs_subgraph)
    inputs_subgraph.set("rank", "same")
    inputs_subgraph.set("style", "dashed")
    inputs_subgraph.set("label", "Workflow Inputs")

    input_edges = cast(
        Iterator[rdflib.query.ResultRow],
        self._rdf_graph.query(
            get_input_edges_query, initBindings={"root_graph": self._root_graph_uri}
        ),
    )  # ResultRow because the query is of type SELECT
    for input_row in input_edges:
        n = pydot.Node(
            "",
            fillcolor="#94DDF4",
            style="filled",
            label=urlparse(input_row["input"]).fragment,
            shape="record",
        )
        n.set_name(str(input_row["input"]))
        inputs_subgraph.add_node(n)
        self._dot_graph.add_edge(
            pydot.Edge(
                quote_id_if_necessary(str(input_row["input"])),
                quote_id_if_necessary(str(input_row["step"])),
            )
        )
