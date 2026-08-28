# Extracted from isamplesorg/vocabularies@a67087996f : tools/vocab2md.py
# region: getNarrower (lines 191-208, stratum sparql_interpolated)
# licence of the source repository: see meta.json
import rdflib
PFX = """
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
"""

def getNarrower(g, v, r):
    if v is None:
        q = rdflib.plugins.sparql.prepareQuery(PFX + """SELECT ?s
        WHERE {
            ?s skos:broader ?parent .
        }""")
        qres = g.query(q, initBindings={'parent': r})
    else:
        q = rdflib.plugins.sparql.prepareQuery(PFX + """SELECT ?s
        WHERE {
            ?s skos:inScheme ?vocabulary .
            ?s skos:broader ?parent .
        }""")
        qres = g.query(q, initBindings={'vocabulary': v, 'parent':r})
    res = []
    for row in qres:
        res.append(row[0])
    return res
