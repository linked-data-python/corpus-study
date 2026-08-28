# Extracted from stevereiner/flexible-graphrag@7d885d5379 : flexible-graphrag/rdf/kg_to_rdf_converter.py
# region: KGToRDFConverter._add_lc_node_triples (lines 499-512, stratum add_in_loop)
# licence of the source repository: see meta.json
from rdflib import Graph, URIRef, Literal, Namespace, BNode
from rdflib.namespace import RDF, RDFS, XSD, OWL

def _add_lc_node_triples(self, g: Graph, lc_node, uri: URIRef) -> None:
    """Add rdf:type, rdfs:label, and datatype property triples for an LC Node.

    Reads LC ``Node.type`` (label) and ``Node.id`` (name) directly —
    no LlamaIndex EntityNode creation.
    """
    type_uri = self._type_uri(lc_node.type or "Entity")
    g.add((uri, RDF.type, type_uri))
    g.add((uri, RDFS.label, Literal(lc_node.id)))
    for prop_name, prop_value in (getattr(lc_node, "properties", {}) or {}).items():
        if prop_value is None:
            continue
        pred = self._predicate_uri(prop_name)
        g.add((uri, pred, _make_literal(prop_value, pred_key=prop_name, xsd_type_map=self._xsd_type_map)))
