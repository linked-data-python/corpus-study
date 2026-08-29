# Context shim (see meta.json), for
# boricles/ontosphere@e0555532687745edb6ed24006eca17cd0a13cea8.
#
# _resolve_uri is a module-level helper in the same source file,
# backend/app/services/export_service.py, just below _export_rdf (lines
# 197-205 of that file) -- outside the extracted region's line range
# (91-194), so the region extraction did not capture it. Copied verbatim.
#
# GraphNode/GraphEdge/GraphData are the real @dataclass definitions from
# backend/app/services/graph_service.py (lines 81-101 of that file),
# copied verbatim -- `_export_rdf` only ever reads their fields, so nothing
# beyond the field shapes is needed; GraphService (the async DB-backed
# class that produces a GraphData) is out of scope, this region receives
# graph_data already built.
from dataclasses import dataclass, field
from typing import Any


def _resolve_uri(uri_or_fragment: str, namespace: "Namespace") -> "URIRef":
    """Resolve a URI string: if it looks like a full URI, use it directly;
    otherwise treat it as a fragment in the given namespace."""
    from rdflib import URIRef

    if "://" in uri_or_fragment:
        return URIRef(uri_or_fragment)
    return namespace[uri_or_fragment]


@dataclass
class GraphNode:
    uri: str
    label: str
    description: str = ""
    node_type: str = "class"  # class | property | individual
    properties: dict[str, Any] = field(default_factory=dict)


@dataclass
class GraphEdge:
    source_uri: str
    target_uri: str
    edge_type: str
    label: str = ""
    properties: dict[str, Any] = field(default_factory=dict)


@dataclass
class GraphData:
    nodes: list[GraphNode] = field(default_factory=list)
    edges: list[GraphEdge] = field(default_factory=list)


class GraphService:
    """Empty placeholder: `_export_rdf` never touches GraphService (it is
    the async DB-backed producer of a GraphData, called by the sibling
    `export_ontology`, outside this region) -- imported by name only, so
    the header import in original.py/translated.ldpy still succeeds."""

