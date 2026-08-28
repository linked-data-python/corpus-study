# Extracted from LA3D/cogitarelink-solid@49121503ea : tests/integration/test_substrate_cleanup.py
# region: test_type_index_has_wiki_registrations (lines 211-231, stratum ns_def_local)
# licence of the source repository: see meta.json
import httpx
from rdflib import Graph, Namespace, URIRef
from rdflib.namespace import RDF
POD_URL = _pod_base() + "/vault/"
WIKI = Namespace("https://pod.vardeman.me/vault/ontology/wiki#")

def test_type_index_has_wiki_registrations():
    """Type Index registers the wiki-memory L3 Thing classes → /wiki/* containers.

    D106: the abstract wiki:Page is NOT registered; the concrete Thing classes are
    (skos:Concept, wiki:Source, wiki:WorkingNote, schema:Person/Place/Event/
    Organization/HowTo). Registration routes class → container/shape (D78/D100).
    """
    SOLID = Namespace("http://www.w3.org/ns/solid/terms#")
    SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")
    SCHEMA = Namespace("https://schema.org/")
    ti = httpx.get(POD_URL + "settings/publicTypeIndex",
                   headers={"Accept": "text/turtle"}, timeout=5)
    assert ti.status_code == 200
    g = Graph().parse(data=ti.text, format="turtle", publicID=POD_URL + "settings/publicTypeIndex")
    regs = list(g.subjects(RDF.type, SOLID.TypeRegistration))
    assert len(regs) >= 5, f"Expected 5+ Type Index registrations, found {len(regs)}"
    registered = {str(o) for o in g.objects(predicate=SOLID.forClass)}
    # The wiki-memory L3 concept + a representative schema.org Thing class are routed.
    assert str(SKOS.Concept) in registered, f"skos:Concept not registered: {registered}"
    assert str(WIKI.Source) in registered, f"wiki:Source not registered: {registered}"
    assert str(SCHEMA.Person) in registered, f"schema:Person not registered: {registered}"
