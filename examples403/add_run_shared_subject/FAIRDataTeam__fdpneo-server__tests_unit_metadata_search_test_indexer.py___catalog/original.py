# Extracted from FAIRDataTeam/fdpneo-server@3e72e119ae : tests/unit/metadata/search/test_indexer.py
# region: _catalog (lines 65-70, stratum add_run_shared_subject)
# licence of the source repository: see meta.json
from rdflib import Graph, Literal, URIRef
from rdflib.namespace import RDF
from context_shim import DCT  # context shim -- see meta.json
REC = "http://localhost:8000/catalog/c1"

def _catalog() -> Graph:
    g = Graph()
    s = URIRef(REC)
    g.add((s, RDF.type, URIRef("http://www.w3.org/ns/dcat#Catalog")))
    g.add((s, DCT.title, Literal("Cat")))
    return g
