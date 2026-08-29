# Extracted from eccenca/cmem-plugin-pyshacl@faf59e81de : cmem_plugin_pyshacl/plugin_pyshacl.py
# region: ShaclValidation.add_labels_val (lines 380-427, stratum trav_single_value)
# licence of the source repository: see meta.json
from rdflib import (
    PROV,
    RDF,
    RDFS,
    SH,
    SKOS,
    XSD,
    BNode,
    Graph,
    Literal,
    Namespace,
    URIRef,
)

def add_labels_val(
    self,
    validation_graph: Graph,
    data_graph: Graph,
    shacl_graph: Graph,
    validation_result_uris: list,
) -> tuple:
    """Add labels"""
    self.log.info("Adding labels to validation graph")
    focus_nodes = []
    validation_report_uri = validation_graph.value(
        predicate=RDF.type, object=SH.ValidationReport
    )
    conforms = validation_graph.value(subject=validation_report_uri, predicate=SH.conforms)
    label = f"SHACL validation report, conforms={conforms!s}"
    if validation_report_uri:
        validation_graph.add((validation_report_uri, RDFS.label, Literal(label)))
    for validation_result_uri in validation_result_uris:
        message = str(
            validation_graph.value(subject=validation_result_uri, predicate=SH.resultMessage)
        )
        result_path = validation_graph.value(
            subject=validation_result_uri, predicate=SH.resultPath
        )
        result_path_string = f"{result_path}: " if result_path else ""
        label = Literal(f"SHACL: {result_path_string}{message}")
        validation_graph.add((validation_result_uri, RDFS.label, label))
        if self.include_graphs_labels:
            focus_node = validation_graph.value(
                subject=validation_result_uri, predicate=SH.focusNode
            )
            if self.add_shui_conforms:
                focus_nodes.append(focus_node)
            label = get_label(data_graph, focus_node)
            if label and focus_node:
                validation_graph.add((focus_node, RDFS.label, label))  # type: ignore[arg-type]
            value = validation_graph.value(subject=validation_result_uri, predicate=SH.value)
            if value and isinstance(value, URIRef | BNode):
                label = get_label(data_graph, value)
                if label:
                    validation_graph.add((value, RDFS.label, label))  # type: ignore[arg-type]
            source_shape = validation_graph.value(
                subject=validation_result_uri, predicate=SH.sourceShape
            )
            label = get_label(shacl_graph, source_shape)
            if label:
                validation_graph.add((source_shape, RDFS.label, label))  # type: ignore[arg-type]
    return validation_graph, focus_nodes
