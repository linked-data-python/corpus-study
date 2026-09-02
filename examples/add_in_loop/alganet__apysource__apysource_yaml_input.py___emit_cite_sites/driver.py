"""Validation driver for alganet__apysource__apysource_yaml_input.py___emit_cite_sites.

Establishes semantic equivalence of original.py and translated.ldpy.
"""
from rdflib import Graph, URIRef

from rdfeval.harness import run_pair

FRAG_URI = URIRef("https://alganet.github.io/apysource/example#frag-1")


def _call_multi_sites():
    # Several cite sites, one with a line and one without, to exercise the
    # loop over more than one row and the conditional fifth triple.
    frag_def = {
        "cited_by": [
            {"file": "src/a.py", "line": 12},
            {"file": "src/b.py"},
        ],
    }
    return (Graph(), FRAG_URI, frag_def, "example fragment"), {}


def _call_no_cited_by():
    # No `cited_by` key at all: the function must return without emitting
    # anything.
    frag_def = {}
    return (Graph(), FRAG_URI, frag_def, "example fragment"), {}


VERDICT = run_pair(
    __file__,
    entry='_emit_cite_sites',
    calls=[_call_multi_sites, _call_no_cited_by],
)
