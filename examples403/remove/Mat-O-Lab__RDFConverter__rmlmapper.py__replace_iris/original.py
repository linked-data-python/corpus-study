# Extracted from Mat-O-Lab/RDFConverter@0d81f4d1ba : rmlmapper.py
# region: replace_iris (lines 178-191, stratum remove)
# licence of the source repository: see meta.json
from rdflib import RDF, Graph, Literal, Namespace, URIRef

def replace_iris(old: URIRef, new: URIRef, graph: Graph):
    # replaces all iri of all triple in a graph with the value of relation
    old_triples = list(graph[old:None:None])
    for triple in old_triples:
        graph.remove((old, triple[0], triple[1]))
        graph.add((new, triple[0], triple[1]))
    old_triples = list(graph[None:None:old])
    for triple in old_triples:
        graph.remove((triple[0], triple[1], old))
        graph.add((triple[0], triple[1], new))
    old_triples = list(graph[None:old:None])
    for triple in old_triples:
        graph.remove((triple[0], old, triple[1]))
        graph.add((triple[0], new, triple[1]))
