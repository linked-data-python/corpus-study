# Extracted from Brasidata/brasidatacenter@e9f8d73d3e : src/brasidatacenter/tool/plugin/command/tool.py
# region: ToolCommand._property_nodes (lines 164-191, stratum trav_one_step)
# licence of the source repository: see meta.json
from rdflib import BNode, Graph, URIRef
from rdflib.namespace import OWL, RDF, RDFS
from brasidatacenter.cli.domain.command import (
    CommandMetadata,
    CommandPort,
    CommandResponse,
    CommandTab,
    CommandTreeNode,
)

@classmethod
def _property_nodes(
    cls,
    graph: Graph,
    properties: set[URIRef],
) -> tuple[CommandTreeNode, ...]:
    return tuple(
        CommandTreeNode(
            label=cls._term_name(graph, property_subject),
            children=tuple(
                CommandTreeNode(
                    label=(
                        "Anonymous range"
                        if isinstance(range_value, BNode)
                        else cls._term_name(graph, range_value)
                    )
                )
                for range_value in sorted(
                    set(graph.objects(property_subject, RDFS.range)),
                    key=str,
                )
            ),
        )
        for property_subject in sorted(
            properties,
            key=lambda subject: cls._term_name(graph, subject).casefold(),
        )
    )
