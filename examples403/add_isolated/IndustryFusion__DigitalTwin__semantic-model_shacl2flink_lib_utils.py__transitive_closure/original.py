# Extracted from IndustryFusion/DigitalTwin@3b40088b88 : semantic-model/shacl2flink/lib/utils.py
# region: transitive_closure (lines 1067-1127, stratum add_isolated)
# licence of the source repository: see meta.json
from rdflib import Graph, RDFS, RDF, OWL, XSD, Literal, SH, Namespace, BNode
from collections import deque

def transitive_closure(g):
    closure_graph = Graph(store="Oxigraph")
    closure_graph += g

    # Ensure rdfs:subClassOf is defined as an OWL.TransitiveProperty if it is not already defined
    if (RDFS.subClassOf, RDF.type, OWL.TransitiveProperty) not in closure_graph:
        closure_graph.add((RDFS.subClassOf, RDF.type, OWL.TransitiveProperty))

    # Handle subClassOf separately
    # Add reflexive subClassOf relationships for all classes
    for s in closure_graph.subjects(predicate=RDFS.subClassOf):
        if (s, RDFS.subClassOf, s) not in closure_graph:
            closure_graph.add((s, RDFS.subClassOf, s))

    # Add reflexive subClassOf relationships for every element of type rdfs:Class and owl:Class
    for s in closure_graph.subjects(predicate=RDF.type, object=RDFS.Class):
        if (s, RDFS.subClassOf, s) not in closure_graph:
            closure_graph.add((s, RDFS.subClassOf, s))
    for s in closure_graph.subjects(predicate=RDF.type, object=OWL.Class):
        if (s, RDFS.subClassOf, s) not in closure_graph:
            closure_graph.add((s, RDFS.subClassOf, s))

    # Handle other transitive properties
    transitive_properties = set(closure_graph.subjects(predicate=RDF.type, object=OWL.TransitiveProperty))
    for prop in transitive_properties:
        # Use a queue for BFS for each transitive property
        queue = deque(closure_graph.triples((None, prop, None)))
        visited = set(queue)

        while queue:
            s1, _, o1 = queue.popleft()

            # Find all objects that o1 is related to via the same property
            for _, _, o2 in closure_graph.triples((o1, prop, None)):
                if (s1, prop, o2) not in visited:
                    # Add new inferred triple
                    closure_graph.add((s1, prop, o2))
                    queue.append((s1, prop, o2))
                    visited.add((s1, prop, o2))

    # Handle generalization of rdf:Bag/rdf:Container
    for bag in closure_graph.subjects(predicate=RDF.type, object=RDF.Bag):
        # Add rdf:Bag and rdfs:Container types
        closure_graph.add((bag, RDF.type, RDFS.Container))

        # Collect all rdf:_n properties (e.g., rdf:_1, rdf:_2, etc.)
        members = []
        for p, o in closure_graph.predicate_objects(subject=bag):
            if p.startswith(str(RDF) + "_"):
                members.append(o)
                # Ensure all values are xsd:string literals
                if not isinstance(o, Literal) or o.datatype != XSD.string:
                    closure_graph.set((bag, p, Literal(str(o), datatype=XSD.string)))

        # Add rdfs:member relationships
        if members:
            closure_graph.add((bag, RDFS.member, Literal(members[0], datatype=XSD.string)))
            for member in members[1:]:
                closure_graph.add((bag, RDFS.member, Literal(member, datatype=XSD.string)))

    return closure_graph
