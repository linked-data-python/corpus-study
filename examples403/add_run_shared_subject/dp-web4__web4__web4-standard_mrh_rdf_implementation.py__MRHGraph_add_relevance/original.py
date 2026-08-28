# Extracted from dp-web4/web4@16038c9d58 : web4-standard/mrh_rdf_implementation.py
# region: MRHGraph.add_relevance (lines 154-189, stratum add_run_shared_subject)
# licence of the source repository: see meta.json
from rdflib import Graph, Namespace, Literal, URIRef, BNode
from rdflib.namespace import RDF, XSD
MRH = Namespace("https://web4.foundation/mrh/v1#")
LCT_NS = Namespace("https://web4.foundation/lct/")  # Renamed to avoid collision with LCT class

def add_relevance(self, edge: MRHEdge) -> BNode:
    """Add a relevance relationship to the graph"""
    relevance_node = BNode()

    # Add type
    self.graph.add((relevance_node, RDF.type, MRH.Relevance))

    # Add target
    target_uri = LCT_NS[edge.target_lct]
    self.graph.add((relevance_node, MRH.target, target_uri))

    # Add probability
    self.graph.add((relevance_node, MRH.probability, 
                   Literal(edge.probability, datatype=XSD.decimal)))

    # Add relation
    rel_uri = MRH[edge.relation.value]
    self.graph.add((relevance_node, MRH.relation, rel_uri))

    # Add distance
    self.graph.add((relevance_node, MRH.distance, 
                   Literal(edge.distance, datatype=XSD.integer)))

    # Add decay rate
    self.graph.add((relevance_node, MRH.decay_rate,
                   Literal(edge.decay_rate, datatype=XSD.decimal)))

    # Add conditional dependencies
    if edge.conditional_on:
        for condition in edge.conditional_on:
            self.graph.add((relevance_node, MRH.conditional_on, LCT_NS[condition]))

    # Store edge for traversal
    self.edges.append(edge)

    return relevance_node
