# Extracted from LA3D/cogitarelink-solid@49121503ea : tests/test_frame_model_agreement.py
# region: test_manifest_installs_narrative_and_exemplars_as_pages (lines 146-160, stratum trav_navigation)
# licence of the source repository: see meta.json
#
# ROOT/OVL/_g/OVERLAY_NS are copied verbatim from the top of the real test
# file (context the region extractor could not carry because it lives above
# this region's own line range). `ROOT` is redefined relative to this file
# (the original resolves the real repository's tests/ directory) so `_g`
# reads the manifest checked in alongside this pair, under
# overlays/wiki-memory/manifest.ttl (trimmed verbatim from the repository
# at the pinned commit -- see that file's own header).
from pathlib import Path
from rdflib import Graph, Namespace

ROOT = Path(__file__).resolve().parent
OVL = ROOT / "overlays" / "wiki-memory"
OVERLAY_NS = Namespace("https://pod.vardeman.me/vault/ontology/overlay#")

def _g(p: Path) -> Graph:
    g = Graph(); g.parse(p, format="turtle"); return g

EXPECTED_PAGES = [
    ("wiki/concepts/how-wiki-memory-works.md", "concepts/how-wiki-memory-works.md"),
    ("wiki/concepts/photosynthesis.md",        "concepts/photosynthesis.md"),
    ("wiki/concepts/biology.md",               "concepts/biology.md"),
    ("wiki/people/marie-curie.md",             "people/marie-curie.md"),
]

def test_manifest_installs_narrative_and_exemplars_as_pages():
    g = _g(OVL / "manifest.ttl")
    # collect (targetResource, body, meta) per installsPage bnode
    entries = []
    for pi in g.objects(None, OVERLAY_NS.installsPage):
        tr = g.value(pi, OVERLAY_NS.targetResource)
        body = g.value(pi, OVERLAY_NS.body)
        meta = g.value(pi, OVERLAY_NS.meta)
        entries.append((str(tr) if tr else "", str(body) if body else "", str(meta) if meta else ""))
    for tr_suf, body_suf in EXPECTED_PAGES:
        match = [e for e in entries if e[0].endswith(tr_suf)]
        assert match, f"no installsPage with targetResource ending {tr_suf}; entries={entries}"
        tr, body, meta = match[0]
        assert body.endswith(body_suf), f"{tr_suf}: body {body!r} should end {body_suf}"
        assert meta.endswith(body_suf + ".meta.ttl"), f"{tr_suf}: meta {meta!r} should end {body_suf}.meta.ttl"

# Demo harness (identical on both sides, see meta.json): the region is a
# pytest test that only ever asserts. `demo` turns a failed assertion into a
# comparable value instead of letting it propagate -- an uncaught
# AssertionError would abort the driver instead of letting both sides be
# compared (same convention as the sibling region
# test_shape_declares_frame in this file).
def demo():
    try:
        test_manifest_installs_narrative_and_exemplars_as_pages()
        return "ok"
    except AssertionError as e:
        return ("assertion-failed", str(e))
