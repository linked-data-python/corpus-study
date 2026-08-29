"""The translator instructions cannot fall behind the language.

An agent starts cold on every batch. Sending it to read nine pages of
`../ldpy/docs/` before writing a line is ~8500 words of the same table, so
the table is inlined into `INSTRUCTIONS.md` instead — GENERATED from
`ldpy.lsp.islanddoc`, which `ldpy/tests/test_islanddoc.py` pins against the
documentation.

Inlining only pays if it cannot rot: a hand-copied reference that lags the
transpiler by two versions is worse than a pointer to the real one, because
it is confidently wrong. Hence this test.
"""

import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "sync_language_reference.py"
INSTRUCTIONS = ROOT / "INSTRUCTIONS.md"


def test_the_inlined_island_reference_is_current():
    pytest.importorskip("ldpy.lsp.islanddoc")
    r = subprocess.run([sys.executable, str(SCRIPT), "--check"],
                       capture_output=True, text=True, cwd=ROOT)
    assert r.returncode == 0, r.stderr or r.stdout


def test_no_agent_facing_document_promises_a_deleted_path():
    """Paths an agent is told to open must exist. A stale `examples403/` or
    `INSTRUCTIONS_403.md` in a batch prompt costs a whole batch."""
    dead = ("examples403", "INSTRUCTIONS_403", "_403.csv", "_403.json",
            "--study 403", "rdfeval sample", "rdfeval regions",
            "rdfeval translate")
    for name in ("INSTRUCTIONS.md", "AGENT_BATCH.md", "README.md"):
        text = (ROOT / name).read_text(encoding="utf-8")
        for token in dead:
            assert token not in text, "%s still mentions %r" % (name, token)


def test_instructions_carry_the_language_reference_inline():
    text = INSTRUCTIONS.read_text(encoding="utf-8")
    assert "BEGIN island-reference" in text
    # the constructions a translator reaches for most, all present
    for form in ("g{ ... }", "m{ ... }", "+{ ... }", "-{ ... }",
                 "@prefix ex: <IRI> .", "?name", "e{ ... }"):
        assert form in text, form
