# Extracted from ScaDS/KGpipe@67ca171cfd : src/kgpipe/evaluation/aspects/func/util.py
# region: extract_cardinality_restrictions (lines 11-27, stratum trav_single_value)
# licence of the source repository: see meta.json
from rdflib import Graph, RDF, OWL
from collections import defaultdict

def extract_cardinality_restrictions(g: Graph):
    restrictions = defaultdict(dict)
    for r in g.subjects(RDF.type, OWL.Restriction):
        prop = g.value(r, OWL.onProperty)

        max_card = g.value(r, OWL.maxCardinality)
        min_card = g.value(r, OWL.minCardinality)
        exact_card = g.value(r, OWL.cardinality)

        if max_card:
            restrictions[prop]["max"] = int(max_card)
        if min_card:
            restrictions[prop]["min"] = int(min_card)
        if exact_card:
            restrictions[prop]["exact"] = int(exact_card)

    return restrictions
