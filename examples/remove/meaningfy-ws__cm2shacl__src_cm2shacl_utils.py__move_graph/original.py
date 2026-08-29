# Extracted from meaningfy-ws/cm2shacl@ec908f3d43 : src/cm2shacl/utils.py
# region: move_graph (lines 14-24, stratum remove)
# licence of the source repository: see meta.json
from rdflib import Graph, URIRef, Literal, BNode, RDF, RDFS, Namespace, SH

def move_graph(identifier_to_remove:list, g_remove:Graph, g_add:Graph):
    for s,p,o in g_remove:
        if s in identifier_to_remove:
            g_remove.remove((s,p,o))
            g_add.add((s,p,o))
            if isinstance(o,BNode):
                move_graph([o], g_remove, g_add)
        elif o in identifier_to_remove:
           g_remove.remove((s,p,o))
           g_add.add((s,p,o))
    return g_remove, g_add
