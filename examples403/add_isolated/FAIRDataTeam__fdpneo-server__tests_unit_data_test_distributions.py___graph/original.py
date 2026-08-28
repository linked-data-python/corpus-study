# Extracted from FAIRDataTeam/fdpneo-server@3e72e119ae : tests/unit/data/test_distributions.py
# region: _graph (lines 27-39, stratum add_isolated)
# licence of the source repository: see meta.json
from rdflib import Graph, URIRef
from fdpneo_server.shared.namespaces import DCAT, DCT
DIST = "https://fdp.example/data/dist-1"
RIGHTS = "https://fdp.example/offers/public"

def _graph(
    *, with_download: bool = True, with_access: bool = True, with_rights: bool = True
) -> Graph:
    g = Graph()
    subject = URIRef(DIST)
    g.add((subject, DCAT.Distribution, URIRef("https://example.org/type")))  # marker triple
    if with_download:
        g.add((subject, DCAT.downloadURL, URIRef("https://files.example.org/d1.csv")))
    if with_access:
        g.add((subject, DCAT.accessURL, URIRef("https://fdp.example/data/dist-1/sparql")))
    if with_rights:
        g.add((subject, DCT.rights, URIRef(RIGHTS)))
    return g
