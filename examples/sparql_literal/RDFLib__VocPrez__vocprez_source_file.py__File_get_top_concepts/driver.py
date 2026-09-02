"""Validation driver for RDFLib__VocPrez__vocprez_source_file.py__File_get_top_concepts.

This region READS a graph (design record corpus/405), but the entry point
takes `self` (`.gr`, `.language`, `.vocab_id`), not a bare graph, so
run_pair's `fixture=` mechanism (which injects ONE parsed graph as the
entry point's sole positional argument) does not apply -- `calls=` builds a
fresh stand-in `self` per call instead, each parsing `fixture.ttl` afresh
(mutable arguments, i.e. graphs, must not leak between the two sides -- see
rdfeval.harness.run_pair's docstring on `calls`).

`get_top_concepts` also reads `g.VOCABS[self.vocab_id]` off Flask's
per-request `g` proxy. Since Flask 0.10, `g` lives on the *application*
context, not the request, so pushing one minimal Flask app's context here
(module scope, before any call) is enough for `g.VOCABS[...]` to resolve
exactly as in the real app -- no shim needed for original.py/translated.ldpy
themselves.

NOT exercised here, and why: when the first query finds nothing (`len(tcs)
== 0`), the function runs a second query wrapped in `GRAPH ?g { ... } UNION
{ ... }`. `self.gr` is a plain `rdflib.Graph` everywhere in the real
project (`File.load_pickle_graph` -> `Graph().parse(...)`, never a
`ConjunctiveGraph`/`Dataset`), and rdflib raises unconditionally when a
`GRAPH` clause is evaluated against a plain `Graph` ("operating currently
on a single graph"), regardless of what the pattern would have matched --
confirmed identically for both the raw query string (original.py) and the
`s{ }` island (translated.ldpy), see meta.json. So in the real project this
fallback branch always crashes, on every vocabulary that has no
`skos:hasTopConcept`/`skos:topConceptOf` triple -- a genuine pre-existing
defect, not a translation artefact. Exercising it here would raise inside
run_pair's `calls` loop, which aborts the ENTIRE verdict on the first
exception rather than reporting a per-case difference, hiding the
successful cases below it. The fixture is built so every call's first
query already finds top concepts, staying clear of that defect.

Each `_case(...)` below returns a plain `(args, kwargs)` tuple, built once
(not a zero-argument callable): `get_top_concepts` only READS `self.gr`, so
there is nothing to protect by handing each side its own fresh graph --
and run_pair also diffs each call's arguments (`call[i].arg[j]`), which for
a callable `case` would otherwise compare two SEPARATELY-CONSTRUCTED
`SimpleNamespace(gr=<fresh Graph>, ...)` stand-ins for `self`. `rdflib.Graph`
has no content-based `__eq__` outside `rdflib.compare` isomorphism, so two
freshly parsed-but-identical graphs compare unequal by identity and every
call would report a false `arg[0]` mismatch having nothing to do with the
translation. Sharing one `self` (and its one graph) between both sides
sidesteps that false alarm and is exact here precisely because the region
never mutates its input.
"""
from types import SimpleNamespace

from flask import Flask, g as flask_g
from rdflib import Graph

from rdfeval.harness import run_pair

_app = Flask(__name__)
_app.app_context().push()


def _case(vocab_id, uri, language):
    flask_g.VOCABS = {vocab_id: SimpleNamespace(uri=uri)}
    gr = Graph().parse("fixture.ttl", format="turtle")
    self_obj = SimpleNamespace(gr=gr, language=language, vocab_id=vocab_id)
    return ((self_obj,), {})


VERDICT = run_pair(
    __file__,
    entry='get_top_concepts',
    calls=[
        _case("v1", "http://example.org/scheme1", "en"),
        _case("v1", "http://example.org/scheme1", "fr"),
    ],
)
