# Extracted from FAIRDataTeam/fdpneo-server@3e72e119ae : tests/unit/metadata/test_identifiers.py
# region: TestReconcile.test_explicit_external_ids_preserved (lines 79-87, stratum add_run_shared_subject)
# licence of the source repository: see meta.json
from rdflib import BNode, Graph, Literal, URIRef
from rdflib.namespace import RDF
from fdpneo_server.metadata.identifiers import reconcile_identifiers
from fdpneo_server.shared.namespaces import ADMS, DCAT, DCT, OWL, SKOS, XSD
ID_BASE = "https://w3id.org/myfdp"
CANON = f"{ID_BASE}/catalog/c1"

def test_explicit_external_ids_preserved(self) -> None:
    canon = URIRef(CANON)
    g = Graph()
    g.add((canon, RDF.type, DCAT.Catalog))
    g.add((canon, DCT.identifier, Literal("ACME-2024-001")))
    g.add((canon, SKOS.exactMatch, URIRef("https://doi.org/10.1234/foo")))
    out = reconcile_identifiers(g, canonical_iri=CANON, identifier_base=ID_BASE)
    assert (canon, DCT.identifier, Literal("ACME-2024-001")) in out
    assert (canon, SKOS.exactMatch, URIRef("https://doi.org/10.1234/foo")) in out
