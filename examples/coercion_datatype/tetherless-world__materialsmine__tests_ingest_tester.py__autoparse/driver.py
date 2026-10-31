"""Validation driver for tetherless-world__materialsmine__tests_ingest_tester.py__autoparse.

Establishes semantic equivalence of original.py and translated.ldpy.

Phase 1 (the translator's): run_pair in module-state mode executes both
modules and compares every module value -- here `expected_data`, a dict
holding a list of rdflib Literals, compared term by term (lexical form,
datatype, language) -- over the tree both files build (two matching
elements, one non-matching neighbour).

Phase 2, added by the mutation audit of 2026-10-30: an ElementTree
element's `.text` is a `str` or `None` (an empty element, `<X/>`), and the
phase-1 tree only holds non-empty strings. Both artefacts are re-executed
from temporary copies in which the tree-building block (identical in the
two files, outside the region) is replaced by one whose matching elements
carry the text values `None`, `""`, `"  "` and a non-ASCII string. Then
`Literal(None)` and `f{None}` must agree (both give `Literal('None')`),
and so must `""`: a translation that turned None into `""`
(`f{elem.text or ""}`) or skipped falsy texts would differ here.
"""
import contextlib
import io
import tempfile
from pathlib import Path

from rdfeval.harness import (_compare_value, _emit, _exec_ldpy, _exec_python,
                             run_pair)

HERE = Path(__file__).resolve().parent

# run_pair prints its own verdict line, and rdfeval check reads the FIRST
# one: silence it, so the line that counts is the one emitted below.
with contextlib.redirect_stderr(io.StringIO()):
    VERDICT = run_pair(__file__, entry=None, calls=None)

TREE_BLOCK = '''for text in ("Tension", "Shear"):
    match = ET.Element(_MATCH_TAG)
    match.text = text
    root.append(match)
'''
FALSY_BLOCK = '''for text in (None, "", "  ", "Cisaillement \\u00e9"):
    match = ET.Element(_MATCH_TAG)
    match.text = text
    root.append(match)
'''

if not VERDICT.get("error"):
    extra = []
    with tempfile.TemporaryDirectory() as tmp:
        for name in ("original.py", "translated.ldpy"):
            src = (HERE / name).read_text()
            if src.count(TREE_BLOCK) != 1:
                extra.append(f"phase 2: tree block not found in {name}")
            (Path(tmp) / name).write_text(src.replace(TREE_BLOCK, FALSY_BLOCK))
        if not extra:
            ns_o = _exec_python(Path(tmp) / "original.py")[0]
            ns_t = _exec_ldpy(Path(tmp) / "translated.ldpy")[0]
            _compare_value(ns_o["expected_data"], ns_t["expected_data"],
                           "phase 2 (None/empty texts): expected_data", extra)
    VERDICT["method"] += " + None/empty texts"
    VERDICT["diffs"] = VERDICT["diffs"] + extra
    VERDICT["equivalent"] = not VERDICT["diffs"]

_emit(VERDICT)
