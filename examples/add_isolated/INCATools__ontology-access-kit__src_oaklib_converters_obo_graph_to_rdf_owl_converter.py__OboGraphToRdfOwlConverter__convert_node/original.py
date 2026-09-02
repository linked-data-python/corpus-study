# Extracted from INCATools/ontology-access-kit@5f88047efa : src/oaklib/converters/obo_graph_to_rdf_owl_converter.py
# region: OboGraphToRdfOwlConverter._convert_node (lines 92-111, stratum add_isolated)
# licence of the source repository: see meta.json
import rdflib
from rdflib import OWL, RDF, RDFS
from context_shim import (
    Edge,
    Graph,
    GraphDocument,
    Meta,
    Node,
    PropertyTypeEnum,
    PropertyValue,
)

def _convert_node(self, source: Node, target: rdflib.Graph) -> rdflib.Graph:
    uri = self._uri_ref(source.id)
    if not source.type or source.type == "CLASS":
        target.add((uri, RDF.type, OWL.Class))
    elif source.type == "PROPERTY":
        if source.propertyType == PropertyTypeEnum.OBJECT:
            target.add((uri, RDF.type, OWL.ObjectProperty))
        elif source.propertyType == PropertyTypeEnum.ANNOTATION:
            target.add((uri, RDF.type, OWL.AnnotationProperty))
        elif source.propertyType == PropertyTypeEnum.DATA:
            target.add((uri, RDF.type, OWL.DatatypeProperty))
    elif source.type == "INDIVIDUAL":
        target.add((uri, RDF.type, OWL.NamedIndividual))
    else:
        raise ValueError(f"Unknown node type: {source.type}")
    if source.lbl:
        target.add((uri, RDFS.label, rdflib.Literal(source.lbl)))
    if source.meta:
        self._convert_meta(uri, source.meta, target=target)
    return target
