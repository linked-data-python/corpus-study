# Extracted from altunelyusuf/SemanticTechnologies@bad0fa7c46 : landscape/07-tooling/build_page_v4_0_0.py
# region: <module> (lines 53-53, stratum add_run_shared_subject)
# licence of the source repository: see meta.json
from page_context import HERE  # context shim, see meta.json
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, RDFS, OWL, SKOS, DCTERMS, XSD, PROV
g = Graph().parse(f"{HERE}/04-page/semtech_page_abox_v3_0_0.ttl")
ONT = URIRef("http://example.org/semtech/page")

g.add((ONT, RDFS.label, Literal("Semantic technology landscape interactive page ABox v4.0.0", lang="en")))
