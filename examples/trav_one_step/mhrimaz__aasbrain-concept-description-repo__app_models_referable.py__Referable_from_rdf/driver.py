"""Validation driver for mhrimaz__aasbrain-concept-description-repo__app_models_referable.py__Referable_from_rdf.

This region READS a graph, so the oracle is not isomorphism but the equality
of the values both versions produce from the same input graph (design record
corpus/405).  `fixture.ttl` is parsed fresh for each side.

`from_rdf` takes two arguments (graph, subject), so we build the calls
ourselves rather than relying on the single-argument `fixture=` shortcut.
"""
from pathlib import Path
from rdflib import URIRef
from rdfeval.harness import run_pair, fixture_graph

_HERE = Path(__file__).resolve().parent
_SUBJECT = URIRef("http://example.org/subject")
_NO_CATEGORY = URIRef("http://example.org/noCategory")

VERDICT = run_pair(
    __file__,
    entry='from_rdf',
    calls=[
        lambda: ((fixture_graph(_HERE / "fixture.ttl"), _SUBJECT), {}),
        lambda: ((fixture_graph(_HERE / "fixture.ttl"), _NO_CATEGORY), {}),
    ],
)
