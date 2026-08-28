# Extracted from tableau/altimeter@efe383f3e1 : altimeter/core/graph/links.py
# region: TagLink.to_rdf (lines 241-261, stratum coercion_datatype)
# licence of the source repository: see meta.json
from rdflib import BNode, Graph, Literal, Namespace, RDF, URIRef, XSD
from altimeter.core.graph.node_cache import NodeCache

def to_rdf(
    self, subj: BNode, namespace: Namespace, graph: Graph, node_cache: NodeCache
) -> None:
    """Graph this link on a BNode in a Graph using a given Namespace to create the full
    predicate.

    Args:
         subj: subject portion of triple - graph this link's pred, obj against it.
         namespace: RDF namespace to use for this triple's predicate
         graph: RDF graph
         node_cache: NodeCache to use to find cached nodes.
    """
    tag_id = f"{self.pred}:{self.obj}"
    tag_node = node_cache.get(tag_id)
    if tag_node is None:
        tag_node = BNode()
        graph.add((tag_node, namespace.key, Literal(self.pred)))
        graph.add((tag_node, namespace.value, Literal(self.obj)))
        graph.add((tag_node, RDF.type, getattr(namespace, "tag")))
        node_cache[tag_id] = tag_node
    graph.add((subj, getattr(namespace, "tag"), tag_node))
