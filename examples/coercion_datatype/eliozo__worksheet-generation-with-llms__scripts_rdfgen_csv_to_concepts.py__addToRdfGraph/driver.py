"""Validation driver for eliozo__worksheet-generation-with-llms__scripts_rdfgen_csv_to_concepts.py__addToRdfGraph.

`addToRdfGraph(g, conceptID, termLV, descLV, termEN=None)` mutates `g` in
place and returns nothing, so the driver compares the `g` argument itself
(isomorphism) after the call. Each call is a lambda factory, invoked once
per side, so the two sides never mutate the same Graph() instance (see
rdfeval.harness.run_pair's own note on mutable arguments).

CALL_1 -- termEN=None: exercises the `if not termEN: termEN = conceptID...`
fallback branch, and a hyphenated conceptID ("foo-bar") through the
`eliozo:{"TRM-" + conceptID}` computed prefixed name -- plain string
concatenation, not percent-encoding, matching original.py's own
`eliozo_ns + "TRM-" + conceptID` exactly (see meta.json). descLV is a real
value: exercises the descLV triple.

CALL_2 -- termEN given explicitly, descLV="": the empty-string branch of
`if descLV and descLV != "" and descLV != "NA":` -- no descLV triple.

CALL_3 -- descLV="NA": the third guard of the same condition -- no descLV
triple either, with a different conceptID/termLV/termEN combination so the
run is not just CALL_2 with one field swapped.

Added by the mutation audit of 2026-10-30, with inputs of the shape the
repository really passes (produceCSVtoRDF: every cell comes from
csv.reader, so a str; termEN is `row[termEN_col]` or None):

CALL_4 -- termEN="" (an empty TitleEn cell): falsy but not None, so the
fallback branch runs; `if termEN is None:` would write `""@en` instead.

CALL_5 -- the graph produceCSVtoRDF really builds, with its two bind()s
(skos, eliozo) before the call. After run_pair, a second phase runs every
call again and compares the prefix bindings of `g`: the repository
serialises that graph (`g.serialize(destination=out_file)`), so `@graph g`
must not replace a binding the original's graph has (it may add the
block's own, record ldpy/027).
"""
import contextlib
import io
from pathlib import Path

import rdflib
from rdflib import Graph

from rdfeval.harness import _emit, _exec_ldpy, _exec_python, run_pair

HERE = Path(__file__).resolve().parent


def _repo_graph():
    """The graph of produceCSVtoRDF (csv_to_concepts.py), bindings included."""
    g = rdflib.Graph()
    g.bind("skos", "http://www.w3.org/2004/02/skos/core#")
    g.bind("eliozo", "http://www.dudajevagatve.lv/eliozo#")
    return g


CALLS = [
    lambda: ((Graph(), "foo-bar", "kāds termins", "kāds apraksts"), {}),
    lambda: ((Graph(), "baz", "cits vārds", ""), {"termEN": "Explicit EN"}),
    lambda: ((Graph(), "qux", "trešais vārds", "NA"), {"termEN": "Another EN"}),
    lambda: ((Graph(), "empty-en", "tukšs", "apraksts"), {"termEN": ""}),
    lambda: ((_repo_graph(), "repo-graph", "termins", "apraksts"), {"termEN": "Term"}),
]

# run_pair prints its own verdict line, and rdfeval check reads the FIRST
# one: silence it, so the line that counts is the one emitted below.
with contextlib.redirect_stderr(io.StringIO()):
    VERDICT = run_pair(__file__, entry='addToRdfGraph', calls=CALLS)

if not VERDICT.get("error"):
    extra = []
    fo = _exec_python(HERE / "original.py")[0]["addToRdfGraph"]
    ft = _exec_ldpy(HERE / "translated.ldpy")[0]["addToRdfGraph"]
    for i, make in enumerate(CALLS):
        (go, *rest), kw = make()
        (gt, *_rest), _kw = make()
        fo(go, *rest, **kw)
        ft(gt, *rest, **kw)
        lost = sorted({(p, str(u)) for p, u in go.namespaces()}
                      - {(p, str(u)) for p, u in gt.namespaces()})
        if lost:
            extra.append(f"call[{i}]: prefix bindings of the original lost "
                         f"in the translation: {lost}")
    VERDICT["method"] += " + g bindings"
    VERDICT["diffs"] = VERDICT["diffs"] + extra
    VERDICT["equivalent"] = not VERDICT["diffs"]

_emit(VERDICT)
