# Extracted from common-workflow-language/cwltool@9f6fcba256 : cwltool/cwlviewer.py
# region: CWLViewer._set_inner_edges (lines 51-111, stratum bind_initbindings)
# licence of the source repository: see meta.json
from collections.abc import Iterator
from typing import cast
from urllib.parse import urlparse
import pydot
import rdflib

def _set_inner_edges(self) -> None:
    get_inner_edges_query = _get_inner_edges_query()
    inner_edges = cast(
        Iterator[rdflib.query.ResultRow],
        self._rdf_graph.query(
            get_inner_edges_query, initBindings={"root_graph": self._root_graph_uri}
        ),
    )  # ResultRow because the query is of type SELECT
    for inner_edge_row in inner_edges:
        source_label = (
            inner_edge_row["source_label"]
            if inner_edge_row["source_label"] is not None
            else urlparse(inner_edge_row["source_step"]).fragment
        )
        # Node color and style depend on class
        source_color = (
            "#F3CEA1"
            if inner_edge_row["source_step_class"].endswith("Workflow")
            else "lightgoldenrodyellow"
        )
        source_style = (
            "dashed" if inner_edge_row["source_step_class"].endswith("Operation") else "filled"
        )
        n = pydot.Node(
            "",
            fillcolor=source_color,
            style=source_style,
            label=source_label,
            shape="record",
        )
        n.set_name(str(inner_edge_row["source_step"]))
        self._dot_graph.add_node(n)
        target_label = (
            inner_edge_row["target_label"]
            if inner_edge_row["target_label"] is not None
            else urlparse(inner_edge_row["target_step"]).fragment
        )

        target_color = (
            "#F3CEA1"
            if inner_edge_row["target_step_class"].endswith("Workflow")
            else "lightgoldenrodyellow"
        )
        target_style = (
            "dashed" if inner_edge_row["target_step_class"].endswith("Operation") else "filled"
        )
        n = pydot.Node(
            "",
            fillcolor=target_color,
            style=target_style,
            label=target_label,
            shape="record",
        )
        n.set_name(str(inner_edge_row["target_step"]))
        self._dot_graph.add_node(n)
        self._dot_graph.add_edge(
            pydot.Edge(
                quote_id_if_necessary(str(inner_edge_row["source_step"])),
                quote_id_if_necessary(str(inner_edge_row["target_step"])),
            )
        )
