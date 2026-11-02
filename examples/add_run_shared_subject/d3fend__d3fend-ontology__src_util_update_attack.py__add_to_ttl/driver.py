"""Validation driver for d3fend__d3fend-ontology__src_util_update_attack.py__add_to_ttl.

Calls add_to_ttl on a fresh graph for each of the three branches of the
function (neither / deprecated / revoked), on the enterprise framework and
on "ics" (where the function also writes skos:prefLabel and the label gets
its suffix), with and without a description-derived deprecation comment, and
with a graph that already holds a tactic superclass of the technique which
ensure_superclasses must drop (a neighbour the region reads indirectly).
The function returns its key and mutates the graph argument: both are
compared.
"""
from rdflib import Graph, Literal, URIRef, RDFS

from rdfeval.harness import run_pair

D3F = "http://d3fend.mitre.org/ontologies/d3fend.owl#"


def _graph():
    g = Graph()
    # a stale tactic superclass, to be removed by ensure_superclasses ...
    g.add((URIRef(D3F + "T1000"), RDFS.subClassOf, URIRef(D3F + "ExecutionTechnique")))
    # ... and a neighbouring technique that must be left alone
    g.add((URIRef(D3F + "T2000"), RDFS.label, Literal("Neighbour")))
    return g


def _tech(id_, **kw):
    t = {
        "id": id_,
        "label": "Technique " + id_,
        "superclasses": ["DiscoveryTechnique", "ImpactTechnique"],
        "revoked_by": None,
        "deprecated": False,
        "revoked": False,
        "data": {"x_mitre_is_subtechnique": False, "description": ""},
    }
    t.update(kw)
    return t


def _call(tech, framework="enterprise"):
    return lambda: ((tech, _graph(), framework), {})


VERDICT = run_pair(
    __file__,
    entry="add_to_ttl",
    calls=[
        _call(_tech("T1000")),
        _call(_tech("T1001", deprecated=True)),
        _call(_tech("T1002", deprecated=True,
                    data={"x_mitre_is_subtechnique": False,
                          "description": "This technique is deprecated, use T1003.\nMore."})),
        _call(_tech("T1003", revoked=True, revoked_by="T1004")),
        _call(_tech("T1005.001", superclasses="T1005",
                    data={"x_mitre_is_subtechnique": True, "description": ""})),
        _call(_tech("T0801"), "ics"),
        _call(_tech("T1406", revoked=True, revoked_by="T1407"), "mobile"),
    ],
)
