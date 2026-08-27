"""End-to-end tests of the mechanical draft, the harness and pair metrics."""

import subprocess
import sys
from pathlib import Path

from rdfeval.compare import measure_pair
from rdfeval.translate import draft_translation

ORIGINAL = """\
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import FOAF

EX = Namespace("http://example.org/")

g = Graph()
g.add((EX.alice, FOAF.name, Literal("Alice", lang="en")))
g.add((EX.alice, FOAF.knows, EX.bob))
g.add((EX.bob, FOAF.name, Literal("Bob", lang="en")))
g.add((EX.bob, FOAF.mbox, URIRef("mailto:bob@example.org")))
"""


def test_draft_translation_produces_valid_ldpy():
    from ldpy.transpiler import transpile
    draft, notes = draft_translation(ORIGINAL)
    assert "@prefix ex: <http://example.org/> ." in draft
    assert "@prefix foaf: <http://xmlns.com/foaf/0.1/> ." in draft
    assert "g += g{" in draft
    assert "URIRef" not in draft.replace("from rdflib import Graph, Literal, Namespace, URIRef", "")
    transpile(draft)            # must be syntactically valid ldpy


def test_draft_is_semantics_preserving():
    """The mechanical draft of ORIGINAL builds an isomorphic graph."""
    from ldpy.transpiler import transpile
    from rdflib.compare import to_isomorphic
    draft, _ = draft_translation(ORIGINAL)
    ns1: dict = {}
    exec(compile(ORIGINAL, "orig", "exec"), ns1)
    ns2: dict = {}
    exec(compile(transpile(draft).code, "draft", "exec"), ns2)
    assert to_isomorphic(ns1["g"]) == to_isomorphic(ns2["g"])


def test_measure_pair_shows_reduction():
    draft, _ = draft_translation(ORIGINAL)
    pair = measure_pair(ORIGINAL, draft)
    assert pair["python"]["triples_added"] == 4
    assert pair["ldpy"]["triples_semantic"] == 4
    assert pair["ratios"]["tokens"] < 1.0
    assert pair["ldpy"]["corr_scaffolding_tokens_per_triple"] \
        < pair["python"]["corr_scaffolding_tokens_per_triple"]


def test_harness_module_state(tmp_path):
    ex = tmp_path / "example"
    ex.mkdir()
    (ex / "original.py").write_text(ORIGINAL)
    draft, _ = draft_translation(ORIGINAL)
    (ex / "translated.ldpy").write_text(draft)
    (ex / "driver.py").write_text(
        "from rdfeval.harness import run_pair\n"
        "run_pair(__file__)\n")
    proc = subprocess.run([sys.executable, str(ex / "driver.py")],
                          capture_output=True, text=True, cwd=ex, timeout=60)
    assert "RDFEVAL-VERDICT" in proc.stderr
    import json
    verdict = json.loads(proc.stderr.split("RDFEVAL-VERDICT ", 1)[1].splitlines()[0])
    assert verdict["equivalent"] is True, verdict


def test_harness_detects_difference(tmp_path):
    ex = tmp_path / "example"
    ex.mkdir()
    (ex / "original.py").write_text(ORIGINAL)
    wrong = ORIGINAL.replace('Literal("Bob", lang="en")', 'Literal("Eve", lang="en")')
    (ex / "translated.ldpy").write_text(wrong)
    (ex / "driver.py").write_text(
        "from rdfeval.harness import run_pair\n"
        "run_pair(__file__)\n")
    proc = subprocess.run([sys.executable, str(ex / "driver.py")],
                          capture_output=True, text=True, cwd=ex, timeout=60)
    import json
    verdict = json.loads(proc.stderr.split("RDFEVAL-VERDICT ", 1)[1].splitlines()[0])
    assert verdict["equivalent"] is False
