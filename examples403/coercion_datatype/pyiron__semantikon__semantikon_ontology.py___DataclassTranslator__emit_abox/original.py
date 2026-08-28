# Extracted from pyiron/semantikon@cfd1d3ffe5 : semantikon/ontology.py
# region: _DataclassTranslator._emit_abox (lines 1213-1250, stratum coercion_datatype)
# licence of the source repository: see meta.json
from typing import Any, TypeAlias, cast
from rdflib import OWL, RDF, RDFS, BNode, Graph, Literal, Namespace, URIRef
QUDT: Namespace = Namespace("http://qudt.org/schema/qudt/")

def _emit_abox(
    self,
    *,
    graph: Graph,
    parent: URIRef,
    field_node: URIRef,
    field_class: URIRef,
    metadata: dict,
    value: Any,
) -> None:
    """
    Emit ABox assertions for a dataclass field.

    Args:
        graph: Graph to populate.
        field_node: Individual representing the field value.
        field_class: Class of the field.
        metadata: Parsed annotation metadata.
        value: Python value of the field.
    """
    graph.add((parent, SNS.has_part, field_node))
    graph.add((field_node, RDF.type, field_class))
    graph.add((field_node, RDFS.label, self._to_field_label(field_node)))
    graph.add(
        (field_node, SNS.local_identifier, Literal(field_node.split("-")[-1]))
    )

    units = metadata.get("units", metadata.get("unit"))
    if units is not None:
        graph.add((field_node, QUDT.hasUnit, _units_to_uri(units)))

    if "uri" in metadata:
        instance = URIRef(str(field_node) + "_uri")
        graph.add((instance, RDF.type, metadata["uri"]))
        graph.add((field_node, SNS.specifies_value_of, instance))

    if value is not None:
        graph.add((field_node, SNS.has_value, Literal(value)))
