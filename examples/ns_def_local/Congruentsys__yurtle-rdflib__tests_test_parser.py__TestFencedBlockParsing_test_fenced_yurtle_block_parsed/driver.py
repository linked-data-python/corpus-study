"""Validation driver for
Congruentsys__yurtle-rdflib__tests_test_parser.py__TestFencedBlockParsing_test_fenced_yurtle_block_parsed.

The region is a pytest test method: `self` and `sample_doc_with_fenced_blocks`
are its parameters, the second injected by a pytest fixture
(tests/conftest.py) rather than passed explicitly. Neither original.py nor
translated.ldpy uses `self`, so `None` stands in for it; the fixture text is
transcribed verbatim into fixture.md (see that file's header) and read once
per side (mutable-argument hygiene: a fresh read per call, even though a str
is immutable here).

The original test only asserts and returns nothing, which would give
run_pair nothing to compare (a hollow green: `None == None` says nothing
about the translation). Both original.py and translated.ldpy therefore end
with `return len(status_changes)` -- exactly the count the original
assertion already checks -- so the driver compares that instead
(entry=/calls=, not fixture=: the region does not take a graph argument, it
builds one from fixture.md, so the fixture= convenience -- which parses a
Turtle file straight into the entry point's sole argument -- does not apply
here).

fixture.md carries both a distractor block (a ```turtle block about
ylayer:Feature, which must NOT match kb:statusChange) and the one block that
should match, so a broken translation of `kb:statusChange` -- to the wrong
predicate, or to a value that never resolves -- changes the returned count
from 1 to 0 rather than passing by accident.

Two more documents, verbatim from the repository's tests/conftest.py, give
the ZERO-solution case through both parser branches: `sample_yaml_doc`
(YAML frontmatter, no fenced block) and
`sample_doc_no_frontmatter_with_block` (no frontmatter, a ```turtle block
without kb:). There the assertion fails on both sides, and the harness
compares the two AssertionErrors (type and message).

A count alone does not see WHICH predicate the region asks for: fixture.md
holds exactly one kb:statusChange, one kb:status, one kb:at and one kb:by
triple, so `kb:status` in place of `kb:statusChange` also returns 1. So,
on top of the run_pair calls, the driver runs each side once more per
document with `YurtleParser` replaced IN THAT SIDE'S MODULE GLOBALS by a
subclass whose parsed graph records every `triples()` call: the pattern
asked for and the triples returned (blank nodes normalised by the
harness). The subclass changes nothing else (the shim's parser runs
unchanged), it is the same on both sides, and each side has its own log.
These extra diffs are merged into the single verdict run_pair emits.
"""
from pathlib import Path

from rdfeval import harness
from rdfeval.harness import run_pair

HERE = Path(__file__).resolve().parent
_DOC_TEXT = (HERE / "fixture.md").read_text(encoding="utf-8")

# tests/conftest.py, fixture sample_yaml_doc (verbatim)
_YAML_DOC = """---
id: T-002
title: YAML Task
status: in-progress
priority: 2
tags:
  - test
  - yaml
---

# T-002: YAML Task

This task uses YAML frontmatter.
"""

# tests/conftest.py, fixture sample_doc_no_frontmatter_with_block (verbatim)
_NO_FRONTMATTER_WITH_BLOCK = """# Standalone Notes

Some notes with an inline knowledge block.

```turtle
@prefix note: <https://nusy.dev/note/> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

<#observation-1> a note:Observation ;
    rdfs:label "Interesting finding" .
```
"""

DOCS = [_DOC_TEXT, _YAML_DOC, _NO_FRONTMATTER_WITH_BLOCK]


def case(text):
    def make():
        return ((None, text), {})
    return make


def _recording_parser(base, log):
    class RecordingParser(base):
        def parse(self, *args, **kwargs):
            doc = super().parse(*args, **kwargs)
            real = doc.graph.triples

            def triples(pattern, *a, **kw):
                found = list(real(pattern, *a, **kw))
                log.append((pattern, found))
                return iter(found)

            doc.graph.triples = triples
            return doc
    return RecordingParser


def _recorded_runs():
    diffs = []
    for i, text in enumerate(DOCS):
        sides = []
        for exec_side, name in ((harness._exec_python, "original.py"),
                                (harness._exec_ldpy, "translated.ldpy")):
            ns, _ = exec_side(HERE / name)
            log = []
            ns["YurtleParser"] = _recording_parser(ns["YurtleParser"], log)
            outcome = harness._outcome(
                ns["test_fenced_yurtle_block_parsed"], (None, text), {})
            sides.append((outcome, log))
        (oo, lo), (ot, lt) = sides
        if oo != ot:
            diffs.append(f"recorded doc[{i}]: outcome differs ({oo!r} vs {ot!r})")
        harness._compare_value(lo, lt, f"recorded doc[{i}]: triples() calls",
                               diffs, ordered=False)
    return diffs


_EXTRA = _recorded_runs()
_emit = harness._emit


def _emit_with_recorder(verdict):
    verdict["diffs"] = list(verdict.get("diffs") or []) + _EXTRA
    verdict["equivalent"] = bool(verdict.get("equivalent")) and not _EXTRA
    _emit(verdict)


harness._emit = _emit_with_recorder

VERDICT = run_pair(__file__, entry="test_fenced_yurtle_block_parsed",
                   calls=[case(text) for text in DOCS])
