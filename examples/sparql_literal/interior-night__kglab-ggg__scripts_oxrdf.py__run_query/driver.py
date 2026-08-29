"""Validation driver for interior-night__kglab-ggg__scripts_oxrdf.py__run_query.

`run_query` returns None: its only observable behaviour is what it prints,
one row per ?item.  That output also carries two `time.time()`-derived
durations, which differ on every single run of the same code -- comparing
raw stdout would report a false diff on a *correct* translation.  So the
graph handed to `run_query` is a thin `Probe` (not an `rdflib.Graph`
subclass -- run_pair special-cases real Graphs for isomorphism only, which
would swallow the very thing this driver needs to check): it delegates
`.query(...)` to a real graph and records the sorted `?item` values that get
consumed, in `.observed`. run_pair then compares that as part of the
argument-equality check, which is exactly the proof of equivalence a
print-only region needs and stdout comparison (out of scope for the `entry=`
call path anyway, see rdfeval.harness) cannot give.

Two calls: a graph rich enough to hit both UNION branches of the query
(one item via the direct owl:onClass branch, one via the double
owl:unionOf/rdf:rest*/rdf:first branch) plus a neighbourhood that must NOT
appear (excluded by each of the four FILTERs and by a missing restriction),
and an empty graph (the zero-solution case).
"""
from rdflib import Graph

import re

from rdfeval.harness import graphs_isomorphic, run_pair

RICH_TTL = """
@prefix ex:   <http://example.org/> .
@prefix owl:  <http://www.w3.org/2002/07/owl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix basf: <https://ontology.basf.net/ontology/BASF_EC_RaMPO/> .

# --- Item1: matches via the FIRST union branch (direct owl:onClass) -------
ex:Item1 rdfs:subClassOf ex:ItemClass1 .
ex:Item1 rdfs:subClassOf [
    a owl:Restriction ; owl:onProperty basf:basedOn ; owl:onClass ex:BaseLayer1
] .
ex:Item1 rdfs:subClassOf [
    a owl:Restriction ; owl:onProperty basf:interactsWith ; owl:onClass ex:InterfaceClass1
] .
ex:Item1 rdfs:label "Item one" .

# --- Item2: matches via the SECOND union branch (both unionOf/rest*/first
#     traversals, plus the hasEquivalentCoatingLayer/someValuesFrom chain) --
ex:Item2 rdfs:subClassOf ex:ItemClass2 .
ex:Item2 rdfs:subClassOf [
    a owl:Restriction ; owl:onProperty basf:basedOn ;
    owl:onClass [ owl:unionOf ( ex:BaseLayer2 ex:OtherBase2 ) ]
] .
ex:Item2 rdfs:subClassOf [
    a owl:Restriction ; owl:onProperty basf:interactsWith ;
    owl:onClass [ owl:unionOf ( ex:InteractsMember2 ex:OtherInteracts2 ) ]
] .
ex:InteractsMember2 rdfs:subClassOf [
    a owl:Restriction ; owl:onProperty basf:hasEquivalentCoatingLayer ;
    owl:someValuesFrom ex:InterfaceClass2
] .

# --- neighbourhood that must NOT appear in the results --------------------

# excluded by FILTER(?item != basf:CoatingLayer): same shape as Item1
basf:CoatingLayer rdfs:subClassOf ex:CoatingLayerClass .
basf:CoatingLayer rdfs:subClassOf [
    a owl:Restriction ; owl:onProperty basf:basedOn ; owl:onClass ex:BaseLayer1
] .
basf:CoatingLayer rdfs:subClassOf [
    a owl:Restriction ; owl:onProperty basf:interactsWith ; owl:onClass ex:InterfaceClass1
] .

# excluded by FILTER(?item != owl:Nothing): same shape as Item1
owl:Nothing rdfs:subClassOf ex:NothingClass .
owl:Nothing rdfs:subClassOf [
    a owl:Restriction ; owl:onProperty basf:basedOn ; owl:onClass ex:BaseLayer1
] .
owl:Nothing rdfs:subClassOf [
    a owl:Restriction ; owl:onProperty basf:interactsWith ; owl:onClass ex:InterfaceClass1
] .

# excluded (both branches need a basf:interactsWith restriction; this class
# only has the basedOn one)
ex:ItemMissingInteracts rdfs:subClassOf ex:ItemClass3 .
ex:ItemMissingInteracts rdfs:subClassOf [
    a owl:Restriction ; owl:onProperty basf:basedOn ; owl:onClass ex:BaseLayer1
] .
"""

EMPTY_TTL = ""


class Probe:
    """Stand-in for the rdflib.Graph run_query is called with: delegates
    .query() to a real graph and records the sorted ?item values consumed
    from each call, since run_pair special-cases a real Graph for
    isomorphism only (see the module docstring)."""

    def __init__(self, graph):
        self._graph = graph
        self.observed = []

    def query(self, *args, **kwargs):
        result = self._graph.query(*args, **kwargs)
        self.observed.append(sorted(str(row.item) for row in result))
        return result

    def __repr__(self):
        return repr(self._graph)

    def __eq__(self, other):
        return (
            isinstance(other, Probe)
            and graphs_isomorphic(self._graph, other._graph)
            and self.observed == other.observed
        )

    def __hash__(self):
        return 0


def _graph(ttl):
    g = Graph()
    if ttl:
        g.parse(data=ttl, format="turtle")
    return g


def call(ttl):
    return lambda: ((Probe(_graph(ttl)),), {})


def drop_nondeterminism(text):
    """What this region prints that is not its meaning.

    The region prints the graph it was handed — whose identifier is a fresh
    UUID per `Graph()` — and its own wall-clock phase timings. Neither is a
    property of the translation. The rest of the output IS compared, and that
    is where the query results are.
    """
    text = re.sub(r"identifier=N[0-9a-f]{32}", "identifier=N<fresh>", text)
    return re.sub(r"time:\s*[\d.]+", "time: <elapsed>", text)


VERDICT = run_pair(
    __file__,
    entry="run_query",
    calls=[call(RICH_TTL), call(EMPTY_TTL)],
    stdout_filter=drop_nondeterminism,
)
