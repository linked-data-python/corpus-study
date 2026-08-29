# Extracted from usc-isi-i2/gaia-knowledge-graph@4bf37bf070 : rdf2json.py
# region: <module> (lines 1-29, stratum sparql_literal)
# licence of the source repository: see meta.json
import json
import rdflib

g = rdflib.Graph()
g.parse("sample1.turtle", format="ttl")

statements = g.query(
        """SELECT DISTINCT ?sub ?pred ?obj
        WHERE {
            { ?s rdf:type rdf:Statement . ?s rdf:predicate ?pred } UNION
            { ?s rdf:type ?pred FILTER (?pred != rdf:Statement) }
            ?s rdf:subject ?sub .
            ?s rdf:object ?obj .
       }""")


d = dict()
for s, p, o in statements:
    d[s] = d.get(s, dict())
    d[s][p] = d[s].get(p, list())
    d[s][p].append(o)

res = list()
for key in d:
    d[key]["uri"] = key
    res.append(d[key])

with open("output.json", "w") as f:
    f.write(json.dumps(res, indent=2))
