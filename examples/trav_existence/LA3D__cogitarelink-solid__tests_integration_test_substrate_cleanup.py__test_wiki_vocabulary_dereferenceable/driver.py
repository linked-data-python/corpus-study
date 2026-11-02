"""Validation driver for LA3D__cogitarelink-solid__tests_integration_test_substrate_cleanup.py__test_wiki_vocabulary_dereferenceable.

EXCLUDED (see meta.json): the region is an integration test of the author's
live Solid Pod. It does `httpx.get("https://pod.vardeman.me/vault/ontology/wiki")`
and asserts a 200 before it ever reaches the graph, so on both sides it ends
on the same network error and the existence reads
`(wiki:Source, rdfs:subClassOf, skos:Concept) in g` are never evaluated.
No fixture can stand in for that without inventing the server's response.

The call below is the region as the study would run it, kept so that the
check reproduces the exact error.
"""
from rdfeval.harness import run_pair

VERDICT = run_pair(
    __file__,
    entry='test_wiki_vocabulary_dereferenceable',
    calls=[((), {})],
)
