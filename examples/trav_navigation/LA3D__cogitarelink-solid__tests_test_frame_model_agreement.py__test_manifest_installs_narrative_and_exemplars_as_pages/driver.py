"""Validation driver for LA3D__cogitarelink-solid__tests_test_frame_model_agreement.py__test_manifest_installs_narrative_and_exemplars_as_pages.

The region reads its graph from a file (`_g(OVL / "manifest.ttl")`), not from
a passed-in graph, so there is no fixture= slot here (see meta.json's
`oracle: isomorphism` -- this is the "supply call arguments" branch of the
protocol, not the fixture.ttl branch): the input graph is a Turtle file
under overlays/<name>/manifest.ttl next to this driver.

`entry` is the `demo` harness both files carry identically (see meta.json):
the region is a pytest test that only ever asserts, so `demo` turns a failed
assertion into a comparable value -- the assertion message -- rather than
letting it abort the driver (same convention as the sibling region
test_shape_declares_frame). `demo(overlay)` rebinds the module global OVL
for one call, so that the driver can vary the manifest the region reads.

Calls, one per manifest:

* wiki-memory: the manifest trimmed from the repository. Several solutions
  (the 4 EXPECTED_PAGES), and neighbourhood that must not match (2 more
  installsPage entries never selected, installsContainer/installsShape on
  the same subject). Expected outcome: "ok".

The others were added by the repair of 2026-10-30; the region is a test,
and its job is to report what is wrong in a manifest, so the message it
fails with is part of its behaviour. Each manifest holds at most one entry
the region lists in a message, so the message does not depend on the order
in which a store yields solutions.

* repair-missing-meta: marie-curie has no overlay:meta. The original keeps
  the entry with meta "" (g.value gives None) and fails on the meta
  assertion. Kills a fused pattern that requires overlay:meta, and a meta
  read widened to any predicate.
* repair-missing-body: one entry without overlay:body -- same, for body.
* repair-missing-target: one entry without overlay:targetResource; the
  original lists it as ('', body, meta). Same, for targetResource.
* repair-other-predicate: a complete entry reached through another
  predicate than overlay:installsPage. Kills installsPage widened to a
  variable.
* repair-empty: no installsPage at all, the zero-solution case.
"""
from rdfeval.harness import run_pair

OVERLAYS = [
    None,                       # overlays/wiki-memory, the repository's own
    "repair-missing-meta",
    "repair-missing-body",
    "repair-missing-target",
    "repair-other-predicate",
    "repair-empty",
]

VERDICT = run_pair(
    __file__,
    entry="demo",
    calls=[((), {}) if o is None else ((o,), {}) for o in OVERLAYS],
)
