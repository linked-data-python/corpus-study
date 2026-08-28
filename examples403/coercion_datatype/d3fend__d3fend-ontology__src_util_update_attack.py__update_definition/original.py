# Extracted from d3fend/d3fend-ontology@cce593d61c : src/util/update_attack.py
# region: update_definition (lines 455-475, stratum coercion_datatype)
# licence of the source repository: see meta.json
from rdflib import BNode, URIRef, Literal, RDF, RDFS, Namespace
from build import get_graph, _xmlns as _XMLNS
d3fend = Namespace("http://d3fend.mitre.org/ontologies/d3fend.owl#")

def update_definition(graph, tech, framework):
    tech = tech["data"]
    attack_id = get_attack_id(tech, framework)
    attack_uri = URIRef(_XMLNS + attack_id)
    new = 0

    if (None, None, Literal(attack_id)) in graph:

        def_property = graph.value(attack_uri, d3fend["definition"])
        # Check if tech already has definition
        if def_property is None:
            new = 1
            # Add definition
            graph.add(
                (
                    attack_uri,
                    d3fend["definition"],
                    Literal(tech["description"].strip().split("\n")[0].strip()),
                )
            )
    return new
