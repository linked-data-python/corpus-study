# Extracted from LA3D/cogitarelink-solid@49121503ea : tests/test_frame_model_agreement.py
# region: test_shape_declares_frame (lines 36-42, stratum trav_existence)
# licence of the source repository: see meta.json
#
# ROOT/OVL/SUB/_g and the other namespaces are copied verbatim from the top
# of the real test file (see meta.json) -- context the region extractor
# could not carry because it lives above the parametrize block, not in the
# region's own line range. `ROOT` is redefined relative to this file (the
# original resolves the real repository's tests/ directory) so `_g` reads
# the shape files checked in alongside this pair, under overlays/.
from pathlib import Path
import pytest
from rdflib import Graph, Namespace

ROOT = Path(__file__).resolve().parent
OVL = ROOT / "overlays" / "wiki-memory"
SUB = Namespace("https://pod.vardeman.me/vault/ontology/substrate#")
SCHEMA = Namespace("https://schema.org/")
SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")
DCT = Namespace("http://purl.org/dc/terms/")
WIKI = Namespace("https://pod.vardeman.me/vault/ontology/wiki#")

def _g(p: Path) -> Graph:
    g = Graph(); g.parse(p, format="turtle"); return g

# (shape_file, shape_iri, frameRole, governsSubject, labelProperty)
FRAMES = [
    ("page.shacl.ttl",    WIKI.PageShape,    "page",    "<>",     DCT.title),
    ("thing.shacl.ttl",   WIKI.ThingShape,   "thing",   "<#this>", SCHEMA.name),
    ("concept.shacl.ttl", WIKI.ConceptShape, "concept", "<#this>", SKOS.prefLabel),
]

@pytest.mark.parametrize("fname,shape,role,subj,labelprop", FRAMES)
def test_shape_declares_frame(fname, shape, role, subj, labelprop):
    g = _g(OVL / "shapes" / fname)
    assert (shape, SUB.frameRole, None) in g, f"{shape} missing sub:frameRole"
    assert str(g.value(shape, SUB.frameRole)) == role
    assert str(g.value(shape, SUB.governsSubject)) == subj
    assert g.value(shape, SUB.labelProperty) == labelprop


# Demo harness (identical on both sides, see meta.json): the region is a
# pytest test that only ever asserts. To exercise the FALSE / zero-solution
# side of `bool(m{ })` as well as the TRUE side (the trav_existence stratum
# is only half-shown by a test that always passes), `demo` calls the region
# and turns a failed assertion into a comparable value instead of letting it
# propagate -- an uncaught AssertionError would abort the driver on the
# first non-matching case rather than let both sides be compared.
def demo(fname, shape, role, subj, labelprop):
    try:
        test_shape_declares_frame(fname, shape, role, subj, labelprop)
        return "ok"
    except AssertionError as e:
        return ("assertion-failed", str(e))
