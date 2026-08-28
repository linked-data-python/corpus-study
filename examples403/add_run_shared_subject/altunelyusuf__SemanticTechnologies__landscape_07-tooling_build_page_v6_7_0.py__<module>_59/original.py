# Extracted from altunelyusuf/SemanticTechnologies@bad0fa7c46 : landscape/07-tooling/build_page_v6_7_0.py
# region: <module> (lines 59-59, stratum add_run_shared_subject)
# licence of the source repository: see meta.json
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, RDFS, OWL, SKOS, DCTERMS, XSD, PROV
g = Graph().parse(f"{HERE}/04-page/semtech_page_abox_v6_6_0.ttl")
ONT = URIRef("http://example.org/semtech/page")

g.add((ONT, RDFS.label, Literal("Semantic technology landscape interactive page ABox v4.0.0", lang="en")))
