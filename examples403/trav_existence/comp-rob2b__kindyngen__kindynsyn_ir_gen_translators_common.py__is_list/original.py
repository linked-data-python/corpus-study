# Extracted from comp-rob2b/kindyngen@414ebd52b2 : kindynsyn/ir_gen/translators/common.py
# region: is_list (lines 43-44, stratum trav_existence)
# licence of the source repository: see meta.json
from rdflib import collection, Graph, URIRef, BNode, Literal, RDF

def is_list(g, x):
    return RDF["first"] in g.predicates(x) and is_bnode(x)
