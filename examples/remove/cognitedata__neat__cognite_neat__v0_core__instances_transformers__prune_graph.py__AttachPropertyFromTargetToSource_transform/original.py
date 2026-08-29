# Extracted from cognitedata/neat@4042d3e96d : cognite/neat/_v0/core/_instances/transformers/_prune_graph.py
# region: AttachPropertyFromTargetToSource.transform (lines 104-152, stratum remove)
# licence of the source repository: see meta.json
from typing import Any, cast
from rdflib import Graph, Namespace, URIRef
from cognite_neat_shim import as_neat_compliant_uri
from cognite_neat_shim import sentence_or_string_to_camel

def transform(self, graph: Graph) -> None:
    nodes_to_delete: list[Any] = []

    if self.target_property_holding_new_property is not None:
        query = self._query_template_use_case_b.format(
            target_node_type=self.target_node_type,
            target_property_holding_new_property_name=self.target_property_holding_new_property,
            target_property=self.target_property,
        )
    else:
        query = self._query_template_use_case_a.format(
            target_node_type=self.target_node_type,
            target_property=self.target_property,
        )

    for (  # type: ignore
        source_node,
        old_predicate,
        target_node,
        new_predicate_value,
        new_property_value,
    ) in graph.query(query):
        if self.target_property_holding_new_property is not None:
            # Ensure new predicate is URI compliant as we are creating a new predicate
            new_predicate_value_string = sentence_or_string_to_camel(str(new_predicate_value))
            predicate = as_neat_compliant_uri(self.namespace[new_predicate_value_string])
        else:
            # this assign seems dangerous
            predicate = old_predicate  # type: ignore
        # Create new connection from source node to value
        graph.add(
            (
                source_node,
                predicate,
                (self.namespace[new_property_value] if self.convert_literal_to_uri else new_property_value),
            )
        )
        # Remove old relationship between source node and destination node
        graph.remove((source_node, old_predicate, target_node))

        nodes_to_delete.append(target_node)

    # this seems a bit funky. Need to check further.
    if self.delete_target_node:
        for target_node in nodes_to_delete:
            # Remove triples with edges to target_node
            graph.remove((None, None, target_node))  # type: ignore
            # Remove target node triple and its properties
            graph.remove((target_node, None, None))  # type: ignore
