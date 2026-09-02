"""Validation driver for BrickSchema__Brick__generate_brick.py__define_classes.

Establishes semantic equivalence of original.py and translated.ldpy by
calling `define_classes` on a small definitions tree that exercises every
branch touched by the region's `add_run_shared_subject` triples: a plain
subclass, a punned class, a nested subclass, an extra `parents` entry, an
alias (which itself walks `graph.objects(...)` to copy `subClassOf`
parents), and a non-list extra property. Each call gets a fresh graph so
mutations on one side cannot leak into the other's.
"""
from rdfeval.harness import run_pair
from rdflib import Graph, URIRef

PARENT = URIRef("https://brickschema.org/schema/Brick#Equipment")

DEFINITIONS = {
    "HVAC": {
        "tags": [],
        "parents": [URIRef("https://brickschema.org/schema/Brick#Asset")],
        "subclasses": {
            "AHU": {},
        },
        "aliases": [URIRef("https://brickschema.org/schema/Brick#AirHandler")],
        URIRef("https://brickschema.org/schema/Brick#hasFlag"):
            URIRef("https://brickschema.org/schema/Brick#Equipment"),
    },
}


def _case():
    g = Graph()
    return ((dict(DEFINITIONS), PARENT), {"pun_classes": True, "graph": g})


VERDICT = run_pair(
    __file__,
    entry='define_classes',
    calls=[_case, _case],
)
