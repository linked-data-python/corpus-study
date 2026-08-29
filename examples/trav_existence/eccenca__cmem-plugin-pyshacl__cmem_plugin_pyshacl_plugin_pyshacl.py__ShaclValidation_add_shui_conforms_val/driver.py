"""Validation driver for eccenca__cmem-plugin-pyshacl__cmem_plugin_pyshacl_plugin_pyshacl.py__ShaclValidation_add_shui_conforms_val.

This region READS a graph, so the oracle is not isomorphism but the equality
of the values both versions produce from the same input graph (design record
corpus/405). `fixture.ttl` is parsed fresh for each side.

The stratifier flagged `subj = i if focus_nodes else
validation_graph.value(subject=i, predicate=SH.focusNode)` (line 436) as
trav_existence, but the value is not thrown away for its truth: it becomes
the subject of the triple `.add()`s next. Per INSTRUCTIONS_403's AVERTISSEMENT
for this stratum, translated with the more specific `.first()`, not
`bool(m{ })` — see meta.json.

Both sides go through `demo(mode, validation_graph, a, b=None)` (see
original.py/translated.ldpy), added identically to both files, because the
region's own `.add()` (or `+{ }`) cannot tolerate a None subject —
`AssertionError`, verified — so the zero-solution case cannot be exercised
through the region's real entry point without crashing before any
comparison happens:

  "mutate" — calls the real, unmodified `add_shui_conforms_val`. Two calls:
    one with two result URIs that both resolve (several solutions across
    the loop), one with focus_nodes given (the branch that never reads).
  "read"   — evaluates just the region's read construction. Two calls:
    ex:result3 (exists, wrong predicate) and ex:result4 (absent from the
    graph entirely) — the zero-solution case, both ways.
"""
from pathlib import Path

from rdflib import URIRef

from rdfeval.harness import run_pair, fixture_graph

FIXTURE = Path(__file__).resolve().parent / "fixture.ttl"
EX = "http://example.org/"


def _mutate(result_uris, focus_nodes):
    ex = lambda n: URIRef(EX + n)
    return lambda: (
        ("mutate", fixture_graph(FIXTURE),
         [ex(n) for n in result_uris], [ex(n) for n in focus_nodes]),
        {},
    )


def _read(result_uri):
    return lambda: (("read", fixture_graph(FIXTURE), URIRef(EX + result_uri)), {})


VERDICT = run_pair(
    __file__,
    entry='demo',
    fixture="fixture.ttl",
    calls=[
        _mutate(["result1", "result2"], []),   # read branch, two solutions
        _mutate([], ["nodeX", "nodeY"]),        # focus_nodes given, no read
        _read("result3"),                       # zero solution: wrong predicate
        _read("result4"),                       # zero solution: absent subject
    ],
)
