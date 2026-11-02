"""Validation driver for isamplesorg__vocabularies__tools_navocab___init__.py__VocabularyStore_load.

`load` is a method; the helper `_load(g, ...)` at the end of both
representations builds a `VocabularyStore` around the graph `g` (see
vocabulary_context.py: upstream opens an SQLAlchemy store, not installed)
and calls it.  `source` is fixture.ttl, an absolute path (identical on both
sides), parsed by the region itself.  What each call shows: the graph `g`
(mutated: parse, prefix bindings, the rdfs:subPropertyOf triple added), what
is printed (the namespace list), the log records, the return value.

Calls:
  * scheme A with the vocabulary of a concept found properly
    (`fixed_concept=True`, see `uri_concept`): A gets rdfs:subPropertyOf B,
    and only B (the same broader concept twice, a broader concept of A
    itself, an untyped concept, a concept without scheme and a neighbour
    scheme are all in the fixture to widen the answer if the pattern or the
    binding is wrong);
  * scheme C, which already extends Z: early return, nothing added;
  * scheme D: concepts but no broader concept at all (zero solutions);
  * scheme A with the REAL `concept` (upstream binds a plain `str` in
    initBindings, which rdflib never matches): nothing is added;
  * scheme A passed as a plain `str`: both queries bind a `str`, nothing
    matches, nothing is added;
  * `voc_uri=None`: the warning branch;
  * `bindings={"ex": ...}`: upstream's `L.debug("binding item k: %", k)` has
    a malformed format string, which raises ValueError once debug records are
    formatted -- compared as a raise; `bindings={}` goes through quietly.
"""
from pathlib import Path

from rdflib import Graph, URIRef

from rdfeval.harness import run_pair

SOURCE = str(Path(__file__).resolve().with_name("fixture.ttl"))
EX = "http://example.org/"


def call(voc, bindings=None, **kw):
    def _make():
        return (Graph(), SOURCE, voc), dict(bindings=bindings, **kw)
    return _make


A, B, C, D = (URIRef(EX + n) for n in ("vocabA", "vocabB", "vocabC", "vocabD"))

VERDICT = run_pair(
    __file__,
    entry='_load',
    calls=[
        call(A, fixed_concept=True),
        call(C, fixed_concept=True),
        call(D, fixed_concept=True),
        call(A),
        call(str(A), fixed_concept=True),
        call(None, fixed_concept=True),
        call(A, bindings={"ex": EX}, fixed_concept=True),
        call(A, bindings={}, fixed_concept=True),
    ],
)
