# Extracted from dp-web4/web4@16038c9d58 : web4-standard/mrh_rdf_implementation.py
# region: MRHGraph.add_relevance (lines 154-189, stratum add_run_shared_subject)
# licence of the source repository: see meta.json
from rdflib import Graph, Namespace, Literal, URIRef, BNode
from rdflib.namespace import RDF, XSD
from context_shim import MRHEdge, MRHGraphStub
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


# Demo harness (identical on both sides, see meta.json): add_relevance takes
# `self` and returns a fresh BNode whose identity is random each run, and
# MRHGraphStub has no __eq__, so comparing `self` as a call argument would
# compare object identity and always fail. This wraps the call in a fresh
# stub per invocation and hands back the graph it wrote to (isomorphism) plus
# the length of self.edges (a plain int, comparable directly).
def demo(edge):
    self = MRHGraphStub()
    add_relevance(self, edge)
    return self.graph, len(self.edges)
