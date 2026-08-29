# Extracted from altunelyusuf/SemanticTechnologies@bad0fa7c46 : landscape/07-tooling/build_core_v6_6_0.py
# region: <module> (lines 72-79, stratum sparql_interpolated)
# licence of the source repository: see meta.json
from rdflib import Graph, Namespace, URIRef, Literal
eg = load("enrichment_g", "v3_0_0")
byid = {n["id"]: n for n in nodes}
errs = []
from rdflib.plugins.sparql import prepareQuery
import json as _json

for cid, (lang, cap, code, check) in eg.SNIPPETS.items():
    if cid not in byid: errs.append(f"snippet class unknown: {cid}")
    try:
        if check == "turtle": Graph().parse(data=eg.SNIPPET_PREFIXES + code, format="turtle")
        elif check == "sparql": prepareQuery("PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> PREFIX ex: <http://example.org/x#>\n" + code)
        elif check == "json": _json.loads(code)
    except Exception as e:
        errs.append(f"snippet invalid: {cid}: {str(e)[:60]}")
