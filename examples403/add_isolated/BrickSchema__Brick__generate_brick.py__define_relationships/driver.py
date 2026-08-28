"""Validation driver for BrickSchema__Brick__generate_brick.py__define_relationships.

The region BUILDS a graph (it mutates the `graph=` keyword argument in
place, and never returns it) so the oracle is RDF isomorphism (meta.oracle
== "isomorphism"), established here on the `graph` kwarg after the call
(run_pair compares kwargs post-call: "une region peut muter son graphe").

`definitions` must be constructed fresh for each of the two calls run_pair
makes (one per side): the region itself mutates it in place via
`propdefn.pop("range"/"datatype"/"domain")`, so a shared dict would answer
the second call with the keys the first call already consumed. Hence a
callable case, not a static (args, kwargs) tuple.

The fixture definitions dict exercises: a property already a URIRef key
(hasPoint) vs. a plain-string key (hasUnit, hasQuantity, hasCount) that
`prop = BRICK[prop]` must convert; recursion via "subproperties" (exercises
the `superprop is not None` -> rdfs:subPropertyOf branch, absent at the top
level); "range" as a list (BNode enumeration + rdf:Collection, via the SHACL
sh:or branch) and as a single value (the sh:class elif branch); "datatype"
equal to BSH.NumericValue (the sh:or branch) and different (the sh:datatype
branch); "domain" as a list; and extra keys of all three shapes
add_relationships itself branches on (a list, a scalar, and a dict which it
silently skips).
"""
from rdflib import BNode, Graph, Literal, URIRef

from brick_context import BRICK, BSH, QUDT, RDF, RDFS, OWL, TAG
from rdfeval.harness import run_pair


def _definitions():
    return {
        BRICK["hasPoint"]: {
            RDF.type: [OWL.ObjectProperty],
            "subproperties": {
                "hasSensor": {
                    RDF.type: [OWL.ObjectProperty],
                },
            },
            "range": [BRICK.Point, BRICK.Sensor],
            "domain": [BRICK.Equipment, BRICK.System],
            BRICK.hasAssociatedTag: [TAG.Point],
            RDFS.label: Literal("has point", lang="en"),
            BRICK.hasQuantity: {"foo": "bar"},  # add_relationships must skip this (a dict)
        },
        "hasUnit": {
            "range": QUDT.Unit,               # single value, not a list
            "domain": BRICK.Quantifiable,
        },
        "hasQuantity": {
            "datatype": BSH.NumericValue,
        },
        "hasCount": {
            "datatype": URIRef("http://example.org/customtype"),
        },
    }


def _case():
    return (), {"definitions": _definitions(), "graph": Graph()}


VERDICT = run_pair(
    __file__,
    entry="define_relationships",
    calls=[_case],
)
