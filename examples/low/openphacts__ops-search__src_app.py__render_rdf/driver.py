"""Validation driver for render_rdf.

The region turns a JSON-LD document (a Python dict, as produced by the
search back end) into a serialisation in the requested format.  The
fixtures below feed representative JSON-LD payloads -- one with an
absolute @id, one relying on relative @id resolution against
``request.url`` (the publicID) -- in two output formats.
"""
from rdfeval.harness import run_pair

DOC = {
    "@context": {
        "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
        "skos": "http://www.w3.org/2004/02/skos/core#",
        "label": "rdfs:label",
    },
    "@id": "http://example.org/compound/aspirin",
    "@type": "skos:Concept",
    "label": "Aspirin",
    "skos:broader": {"@id": "http://example.org/compound/nsaid"},
}

RELATIVE_DOC = {
    "@context": {"rdfs": "http://www.w3.org/2000/01/rdf-schema#"},
    "@id": "item/1",
    "rdfs:label": "relative subject, resolved against publicID",
}


def case(doc, fmt):
    return lambda: ((doc, fmt), {})


VERDICT = run_pair(
    __file__,
    entry="render_rdf",
    calls=[
        case(DOC, "turtle"),
        case(DOC, "nt"),
        case(RELATIVE_DOC, "turtle"),
    ],
)
