# Extracted from technologiestiftung/digital-budget-network-explorer@a2c69bf9f4 : csv_to_ttl.py
# region: build_graph (lines 459-476, stratum ns_def_local)
# licence of the source repository: see meta.json
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import DCTERMS, OWL, RDF, RDFS, SKOS, XSD
SCHEMA = Namespace("https://schema.org/")

if wikidata_links:
    WD = Namespace("http://www.wikidata.org/entity/")
    g.bind("wd", WD)
    for ep, info in wikidata_links.items():
        qid = info.get("qid")
        if not qid:
            continue
        ep_uri = NS_EP[ep]
        # Nur verknuepfen, wenn der Einzelplan im Graphen existiert
        if (ep_uri, RDF.type, SCHEMA.GovernmentOrganization) not in g:
            continue
        wd_uri = WD[qid]
        if info.get("thematic"):
            g.add((ep_uri, RDFS.seeAlso, wd_uri))
        else:
            g.add((ep_uri, OWL.sameAs, wd_uri))
        if info.get("label"):
            g.add((wd_uri, RDFS.label, Literal(info["label"], lang="de")))
