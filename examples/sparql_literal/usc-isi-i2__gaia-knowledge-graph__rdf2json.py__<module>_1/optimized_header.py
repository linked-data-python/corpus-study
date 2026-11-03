# Extracted from usc-isi-i2/gaia-knowledge-graph@4bf37bf070 : rdf2json.py
# region: <module> (lines 1-29, stratum sparql_literal)
# licence of the source repository: see meta.json
import json
import rdflib

g = rdflib.Graph().parse("sample1.turtle", format="ttl")

d = {}
for s, p, o in g.query("""SELECT DISTINCT ?sub ?pred ?obj
        WHERE {
            { ?s a rdf:Statement ; rdf:predicate ?pred } UNION
            { ?s a ?pred FILTER (?pred != rdf:Statement) }
            ?s rdf:subject ?sub ; rdf:object ?obj .
       }"""):
    d.setdefault(s, {}).setdefault(p, []).append(o)

for key in d:
    d[key]["uri"] = key
res = list(d.values())

with open("output.json", "w") as f:
    json.dump(res, f, indent=2)
