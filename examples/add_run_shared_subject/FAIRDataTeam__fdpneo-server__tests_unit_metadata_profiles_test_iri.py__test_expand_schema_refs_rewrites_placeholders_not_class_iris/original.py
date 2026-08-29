# Extracted from FAIRDataTeam/fdpneo-server@3e72e119ae : tests/unit/metadata/profiles/test_iri.py
# region: test_expand_schema_refs_rewrites_placeholders_not_class_iris (lines 55-71, stratum add_run_shared_subject)
# licence of the source repository: see meta.json
import pytest
from rdflib import Graph, URIRef
from rdflib.namespace import RDF
from fdpneo_server.metadata.profiles.iri import IRIExpander, expand_schema_refs, schema_slug
from fdpneo_server.shared.namespaces import DCAT, SH
BASE = "http://localhost:8000"

@pytest.mark.unit
def test_expand_schema_refs_rewrites_placeholders_not_class_iris() -> None:
    g = Graph()
    catalog = URIRef("urn:fdp-schema:catalog")
    g.add((catalog, RDF.type, SH.NodeShape))
    g.add((catalog, SH.targetClass, DCAT.Catalog))  # real class IRI — must stay
    g.add((catalog, SH.node, URIRef("urn:fdp-schema:dataset")))  # placeholder — rewrite

    out = expand_schema_refs(g, BASE)
    cat_iri = URIRef(f"{BASE}/fdp-api/schemas/catalog")
    # Subject + sh:node placeholders → storage IRIs.
    assert (cat_iri, RDF.type, SH.NodeShape) in out
    assert (cat_iri, SH.node, URIRef(f"{BASE}/fdp-api/schemas/dataset")) in out
    # The real vocabulary IRI in sh:targetClass is untouched.
    assert (cat_iri, SH.targetClass, DCAT.Catalog) in out
    # Nothing placeholder-shaped survives.
    assert not any("urn:fdp-schema:" in str(term) for triple in out for term in triple)
