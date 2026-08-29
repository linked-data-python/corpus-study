"""Validation driver for LA3D__cogitarelink-solid__tests_test_frame_model_agreement.py__test_shape_declares_frame.

Establishes semantic equivalence of original.py and translated.ldpy.

The region reads its graph from a file (`_g(OVL / "shapes" / fname)`), not
from a passed-in graph, so there is no fixture.ttl slot here; the input
graphs are the four Turtle files under overlays/wiki-memory/shapes/ next to
this driver (three trimmed from the real repository, see meta.json, plus a
synthetic `broken.shacl.ttl`).

`entry` is the `demo` harness both files carry identically (see meta.json):
the region is a pytest test that only ever asserts, so `demo` turns a failed
assertion into a comparable value rather than letting it abort the driver.
The four calls are the region's own parametrize table (page/thing/concept,
all TRUE for `bool(m{ {shape} sub:frameRole ?fr })`) plus `broken.shacl.ttl`
(FALSE / zero-solution: wiki:BrokenShape has no sub:frameRole at all). The
neighbourhood that must not match sits inside page.shacl.ttl itself:
wiki:PageDraftShape carries the same predicates with a different frameRole.
"""
from rdflib import Namespace

from rdfeval.harness import run_pair

WIKI = Namespace("https://pod.vardeman.me/vault/ontology/wiki#")
DCT = Namespace("http://purl.org/dc/terms/")
SCHEMA = Namespace("https://schema.org/")
SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")

VERDICT = run_pair(
    __file__,
    entry="demo",
    calls=[
        (("page.shacl.ttl", WIKI.PageShape, "page", "<>", DCT.title), {}),
        (("thing.shacl.ttl", WIKI.ThingShape, "thing", "<#this>", SCHEMA.name), {}),
        (("concept.shacl.ttl", WIKI.ConceptShape, "concept", "<#this>", SKOS.prefLabel), {}),
        # zero-solution: wiki:BrokenShape never declares sub:frameRole
        (("broken.shacl.ttl", WIKI.BrokenShape, "page", "<>", DCT.title), {}),
    ],
)
