"""Validation driver for RDFLib__VocPrez__vocprez_source_file.py__File_get_top_concepts.

This region READS a graph (design record corpus/405), but the entry point
takes `self` (`.gr`, `.language`, `.vocab_id`), not a bare graph, so
run_pair's `fixture=` mechanism (which injects ONE parsed graph as the
entry point's sole positional argument) does not apply -- `calls=` passes a
stand-in `self` per call instead.

`get_top_concepts` also reads `g.VOCABS[self.vocab_id]` off Flask's
per-request `g` proxy. Since Flask 0.10, `g` lives on the *application*
context, not the request, so pushing one minimal Flask app's context here
(module scope, before any call) is enough for `g.VOCABS[...]` to resolve
exactly as in the real app -- no shim needed for original.py/translated.ldpy
themselves.  `g.VOCABS` is filled ONCE, with one vocab id per scheme, so
each call reads its own scheme whatever the order of construction.
`vocab.uri` is a plain `str` and `self.language` a `str`, as in the
repository (file.py:98-100, `language or DEFAULT_LANGUAGE`).

Each `_case(...)` returns a plain `(args, kwargs)` tuple, built once (not a
zero-argument callable): `get_top_concepts` only READS `self.gr`, and
run_pair diffs each call's arguments (`call[i].arg[j]`); two separately
parsed graphs compare unequal by identity (`rdflib.Graph.__eq__` compares
identifiers), so a stand-in per side would report a false `arg[0]`
mismatch.  Sharing one `self` between both sides is exact because the
region never mutates its input.

The calls, and what each exercises:

  * call[0], call[1] -- ex:scheme1 on the repository's input type, a plain
    `rdflib.Graph` (fixture.ttl), in "en" then "fr": both UNION branches of
    the FIRST query (hasTopConcept, topConceptOf), the language FILTER and
    its `lang(?pl) = ""` arm, the ORDER BY, the pl_cache de-duplication.
    The fixture holds neighbours sharing two terms with each triple pattern
    (`ex:scheme1 skos:member`, `skos:inScheme ex:scheme1`,
    `skos:topConceptOf ex:scheme2`, `ex:other skos:hasTopConcept`, a "de"
    label): a term widened to a variable lets one of them in.
  * call[2] -- ex:scheme3, which has no top concept, on the plain Graph:
    the first query finds nothing and the FALLBACK query runs; its
    `GRAPH ?g` clause makes rdflib raise on a plain Graph.  This is what
    the repository does for every such vocabulary (`self.gr` comes from
    `load_pickle_graph`, a pickled plain Graph, file.py:560-569).  The
    harness compares the two raises (type and message).
  * call[3] -- a scheme with nothing at all, on the plain Graph: the same
    path through the fallback, from an empty first result.
  * call[4], call[5], call[6] -- the FALLBACK query's text itself, on an
    `rdflib.Dataset` (fixture_dataset.trig) where the `GRAPH ?g` branch
    evaluates: ex:scheme3 in "en" then "fr" (hasTopConcept in the named
    graph, skos:inScheme in both graphs, a no-language label, neighbours
    with skos:topConceptOf, skos:member, another scheme and another
    language that the fallback must not return), and an unknown scheme
    (zero solution in both queries, returns []).  The repository never
    passes a Dataset; these calls exist because otherwise no execution
    would ever compare the fallback query's two versions.
"""
from types import SimpleNamespace

from flask import Flask, g as flask_g
from rdflib import Dataset, Graph

from rdfeval.harness import run_pair

_app = Flask(__name__)
_app.app_context().push()

flask_g.VOCABS = {
    "v1": SimpleNamespace(uri="http://example.org/scheme1"),
    "v3": SimpleNamespace(uri="http://example.org/scheme3"),
    "v9": SimpleNamespace(uri="http://example.org/scheme9"),
}

_GRAPH = Graph().parse("fixture.ttl", format="turtle")
_DATASET = Dataset()
_DATASET.parse("fixture_dataset.trig", format="trig")


def _case(gr, vocab_id, language):
    self_obj = SimpleNamespace(gr=gr, language=language, vocab_id=vocab_id)
    return ((self_obj,), {})


VERDICT = run_pair(
    __file__,
    entry='get_top_concepts',
    calls=[
        _case(_GRAPH, "v1", "en"),
        _case(_GRAPH, "v1", "fr"),
        _case(_GRAPH, "v3", "en"),
        _case(_GRAPH, "v9", "en"),
        _case(_DATASET, "v3", "en"),
        _case(_DATASET, "v3", "fr"),
        _case(_DATASET, "v9", "en"),
    ],
)
