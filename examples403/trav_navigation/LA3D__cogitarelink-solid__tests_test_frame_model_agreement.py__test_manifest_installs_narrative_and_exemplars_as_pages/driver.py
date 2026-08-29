"""Validation driver for LA3D__cogitarelink-solid__tests_test_frame_model_agreement.py__test_manifest_installs_narrative_and_exemplars_as_pages.

The region reads its graph from a file (`_g(OVL / "manifest.ttl")`), not from
a passed-in graph, so there is no fixture= slot here (see meta.json's
`oracle: isomorphism` -- this is the "supply call arguments" branch of the
protocol, not the fixture.ttl branch): the input graph is the Turtle file
under overlays/wiki-memory/manifest.ttl next to this driver (trimmed from
the real repository, see that file's own header).

`entry` is the `demo` harness both files carry identically (see meta.json):
the region is a pytest test that only ever asserts, so `demo` turns a failed
assertion into a comparable value rather than letting it abort the driver
(same convention as the sibling region test_shape_declares_frame). The
function itself is not parametrized -- unlike that sibling there is only one
call. Several solutions of the fused pattern (4 expected installsPage
entries) and neighbourhood that must not match (2 more installsPage entries
EXPECTED_PAGES never selects, plus installsContainer/installsShape on the
same subject) live inside manifest.ttl itself; see meta.json for why a
genuine zero-solution call is not exercised here.
"""
from rdfeval.harness import run_pair

VERDICT = run_pair(
    __file__,
    entry="demo",
    calls=[((), {})],
)
