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

Added by the repair of 2026-10-30, after triage showed that freeing the
subject, or swapping the predicate, of the existence read stayed green
(broken.shacl.ttl has no sub:frameRole at all), and that assertions 2 to 4
were only ever seen true:

  5-6. partial.shacl.ttl, wiki:NoFrameShape: sub:frameRole absent for this
       shape but present for another one in the same graph, and the shape
       has sub:labelProperty -> assertion 1 fails with its message.  Kills
       the mutants `?x sub:frameRole ?fr` and `{shape} sub:labelProperty ?fr`
       on the existence read: call 5 expects role "page" (the mutant then
       fails assertion 2 with an empty message), call 6 expects role "None"
       (the mutant then passes every assertion and returns "ok").
  7.   partial.shacl.ttl, wiki:NoSubjectShape with subj "None" and
       labelprop None: the zero-solution case of the governsSubject and
       labelProperty reads (`str(None) == "None"`, `None == None`) -> "ok".
       `.one()` would raise there, and a leaking subject would read
       NoFrameShape's "<>" / dct:title.
  8.   PageShape with role "draft" -> assertion 2 fails (PageDraftShape's
       value: a subject leak in that read would pass it).
  9.   ThingShape with subj "<>" -> assertion 3 fails.
  10.  ConceptShape with labelprop schema:name -> assertion 4 fails.
       Each of 8-10 makes exactly ONE assertion fail, so a mutant that
       weakens that assertion turns the outcome into "ok".

The real test passes `labelprop` as a Namespace term (a URIRef), and so
does the driver.
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
        # sub:frameRole occurs in the graph, but not for this shape
        (("partial.shacl.ttl", WIKI.NoFrameShape, "page", "<>", DCT.title), {}),
        # same, with the values a missing frameRole would yield further down:
        # a mutant that passes assertion 1 would then pass them all -> "ok"
        (("partial.shacl.ttl", WIKI.NoFrameShape, "None", "<>", DCT.title), {}),
        # zero solutions for governsSubject and labelProperty -> "ok"
        (("partial.shacl.ttl", WIKI.NoSubjectShape, "page", "None", None), {}),
        # exactly one failing assertion each: 2, 3, 4
        (("page.shacl.ttl", WIKI.PageShape, "draft", "<>", DCT.title), {}),
        (("thing.shacl.ttl", WIKI.ThingShape, "thing", "<>", SCHEMA.name), {}),
        (("concept.shacl.ttl", WIKI.ConceptShape, "concept", "<#this>", SCHEMA.name), {}),
    ],
)
