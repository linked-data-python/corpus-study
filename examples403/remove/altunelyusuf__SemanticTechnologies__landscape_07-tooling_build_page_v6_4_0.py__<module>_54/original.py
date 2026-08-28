# Extracted from altunelyusuf/SemanticTechnologies@bad0fa7c46 : landscape/07-tooling/build_page_v6_4_0.py
# region: <module> (lines 54-54, stratum remove)
# licence of the source repository: see meta.json
from rdflib.namespace import RDF, RDFS, OWL, SKOS, DCTERMS, XSD, PROV
g = Graph().parse(f"{HERE}/04-page/semtech_page_abox_v6_3_0.ttl")
ONT = URIRef("http://example.org/semtech/page")

for p in (OWL.versionInfo, OWL.versionIRI, DCTERMS.modified): g.remove((ONT, p, None))
