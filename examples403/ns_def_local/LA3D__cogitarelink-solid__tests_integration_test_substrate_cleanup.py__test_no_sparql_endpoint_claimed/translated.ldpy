# Extracted from LA3D/cogitarelink-solid@49121503ea : tests/integration/test_substrate_cleanup.py
# region: test_no_sparql_endpoint_claimed (lines 195-208, stratum ns_def_local)
# licence of the source repository: see meta.json
import httpx
from rdflib import Graph, Namespace, URIRef
POD_URL = _pod_base() + "/vault/"

def test_no_sparql_endpoint_claimed():
    """Affordance descriptors don't claim /sparql endpoint anymore."""
    hub_url = POD_URL + "meta/affordances/hub-view.ttl"
    r = httpx.get(hub_url, timeout=5)
    assert r.status_code == 200
    g = Graph().parse(data=r.text, format="turtle", publicID=hub_url)
    WIKI_NS = Namespace("https://pod.vardeman.me/vault/ontology/wiki#")
    SUB_NS  = Namespace("https://pod.vardeman.me/vault/ontology/substrate#")
    invoked_at_triples = list(g.triples((None, WIKI_NS.invokedAt, None)))
    assert not invoked_at_triples, (
        f"hub-view should not have wiki:invokedAt; found: {invoked_at_triples}"
    )
    requires_cap_triples = list(g.triples((None, SUB_NS.requiresCapability, None)))
    assert requires_cap_triples, "hub-view should declare sub:requiresCapability"
