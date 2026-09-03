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
"""
from pathlib import Path

from rdfeval.harness import run_pair

HERE = Path(__file__).resolve().parent
_DOC_TEXT = (HERE / "fixture.md").read_text(encoding="utf-8")


def case():
    def make():
        return ((None, _DOC_TEXT), {})
    return make


VERDICT = run_pair(__file__, entry="test_fenced_yurtle_block_parsed", calls=[case()])
