# Extracted from isamplesorg/vocabularies@a67087996f : tools/vocab2md.py
# region: getNarrower (lines 191-208, stratum sparql_interpolated)
# licence of the source repository: see meta.json
PFX = """
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
"""

def getNarrower(g, v, r):
    if v is None:
        qres = g.query(PFX + "SELECT ?s WHERE { ?s skos:broader ?parent . }",
                       initBindings={'parent': r})
    else:
        qres = g.query(
            PFX + "SELECT ?s WHERE { ?s skos:inScheme ?vocabulary . ?s skos:broader ?parent . }",
            initBindings={'vocabulary': v, 'parent': r})
    return [row[0] for row in qres]
