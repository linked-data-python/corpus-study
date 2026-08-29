"""Validation driver for LA3D__cogitarelink-solid__tests_test_interop_foundation.py__test_addressbook_managers_assign_container_trees_and_name_their_container.

This region reads FOUR separate Turtle documents (one per addressbook
manager slug -- person/organization/group/membership), each independently
parsed by the original code (`g = rdflib.Graph(); g.parse(f, ...)`), not one
shared graph: the whole point of `next(g.subjects(RDF.type, ST.Manager))` is
that each manager file holds EXACTLY one `st:Manager`, so the match is
unambiguous. Merging all four into one graph before matching would make
`next()` / `.one()` pick from FOUR candidates -- store-order dependent, not
what the original tests.

`fixture.ttl` holds all four managers' data (plus a decoy assignment),
addressed by synthetic root IRIs (`urn:ex:mgr:<slug>`) instead of the real
files' relative `<>` (four physical files can't share one `<>` in a single
parsed document). This driver parses it once, then re-partitions it into
four isolated per-slug graphs by subject closure from each manager root --
the oracle's equivalent of "read four separate files" -- and passes that
dict as the region's restored `manager_graphs` parameter.

Zero-solution note (see meta.json translation_notes): every read in this
region feeds a bare `assert` inside the SAME function call that `run_pair`
invokes once; run_pair aborts the whole comparison on the first side that
raises (see rdfeval/harness.py) rather than checking whether both sides
raise alike, so a fixture where some manager is missing its assignment
cannot be driven through here -- same limitation already documented on the
sibling region of this batch,
examples403/trav_existence/LA3D__cogitarelink-solid__tests_test_interop_foundation.py__test_registry_chain_covers_all_apps_every_registration_a_container_tree.
"""
from pathlib import Path

from rdfeval.harness import run_pair, fixture_graph
from rdflib import Graph, URIRef

HAS_ASSIGNMENT = URIRef("http://www.w3.org/ns/shapetrees#hasAssignment")
SLUGS = ("person", "organization", "group", "membership")


def _manager_graphs():
    whole = fixture_graph(Path(__file__).parent / "fixture.ttl")
    graphs = {}
    for slug in SLUGS:
        mgr = URIRef(f"urn:ex:mgr:{slug}")
        g = Graph()
        for t in whole.triples((mgr, None, None)):
            g.add(t)
        for a in whole.objects(mgr, HAS_ASSIGNMENT):
            for t in whole.triples((a, None, None)):
                g.add(t)
        graphs[slug] = g
    return graphs


VERDICT = run_pair(
    __file__,
    entry='test_addressbook_managers_assign_container_trees_and_name_their_container',
    calls=[lambda: ((_manager_graphs(),), {})],
)
