# Extracted from isamplesorg/vocabularies@a67087996f : tools/vocab2md.py
# region: getObjects (lines 211-220, stratum sparql_interpolated)
# licence of the source repository: see meta.json
import rdflib
PFX = """
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
"""

def getObjects(g, s, p):
    q = rdflib.plugins.sparql.prepareQuery(PFX + """SELECT ?o
    WHERE {
        ?subject ?predicate ?o .
    }""")
    qres = g.query(q, initBindings={'subject':s, 'predicate':p})
    res = []
    for row in qres:
        res.append(row[0])
    return res
