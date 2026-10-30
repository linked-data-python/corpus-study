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

The first two calls: a graph rich enough to hit both UNION branches of the query
(one item via the direct owl:onClass branch, one via the double
owl:unionOf/rdf:rest*/rdf:first branch) plus a neighbourhood that must NOT
appear (excluded by each of the four FILTERs and by a missing restriction),
and an empty graph (the zero-solution case).

In RICH_TTL every item the second UNION branch finds is also found by the
first one (an owl:onClass on a union is still an owl:onClass), so a mutant of
the second branch, or of a FILTER, stayed invisible.  The SCENARIOS calls fix
that: each is its own small graph in which ONE item is decided by ONE part of
the query.

  * The second branch alone decides an item when its interactsWith
    restriction points owl:onClass at basf:CoatingLayer: the first branch
    then binds ?interfaceClass to basf:CoatingLayer, which the outer FILTER
    rejects, while the second branch binds it to the someValuesFrom class of
    a member of basf:CoatingLayer's owl:unionOf list.
  * b2-index2 / b2-index0: the item's interactsWith member at index 2 / 0 of
    the list, its basedOn list with one element / with the only element that
    passes FILTER(?interfaceClass != ?base_layer) at index 2.  Together they
    tell rdf:rest* from rdf:rest, rdf:rest? and rdf:rest+ in both paths.
  * the other b2-* graphs keep the second branch whole but one term
    (FILTER on ?base_layer, rdf:type owl:Restriction, the onProperty, the
    someValuesFrom, owl:unionOf): the item must NOT appear, and a mutant that
    drops or widens that term makes it appear.
  * the b1-* and top-* graphs do the same for the first branch and the
    outer FILTERs (?item_class, basf:CoatingLayer as ?interfaceClass, the
    basedOn / interactsWith onProperty, the rdf:type of each restriction).
    The OPTIONAL { ?item rdfs:label ?label } is not exercised: ?label is not
    projected and DISTINCT absorbs the rows it could multiply, so removing it
    is an equivalent mutant.  So are two widenings of ?restriction1's
    owl:onClass: the top-level one is repeated inside each branch, and the
    first branch's ?base_layer feeds no FILTER and is not projected.

Finally the KG calls pass what the repository's own script passes the second
time: a kglab.KnowledgeGraph (scripts/oxrdf.py:55-57).  KnowledgeGraph is a
stand-in whose query() is kglab's QueryingMixin.query verbatim
(kglab/query/mixin.py:45-71 in the same repository: keyword-only `bindings`,
no `initBindings`, a generator over self._g.query).  Its default repr carries
an object address, dropped by the stdout filter like the Graph identifier.
On this argument s{ ... }(g) raised TypeError (the island always calls
g.query(prepared, initBindings=...)), where the original iterates: that is
why translated.ldpy keeps g.query(QUDT_QUERY9) (meta.json).
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


PREFIXES = """
@prefix ex:   <http://example.org/> .
@prefix owl:  <http://www.w3.org/2002/07/owl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix basf: <https://ontology.basf.net/ontology/BASF_EC_RaMPO/> .
"""


def b2(base_list="ex:BaseA", members="ex:X ex:Y ex:M", member_restriction=
       "a owl:Restriction ; owl:onProperty basf:hasEquivalentCoatingLayer ; "
       "owl:someValuesFrom ex:IC", union="owl:unionOf",
       r2="a owl:Restriction ; owl:onProperty basf:interactsWith"):
    """An ex:Item that only the SECOND union branch can find (see the module
    docstring), with each term of that branch a parameter."""
    return PREFIXES + f"""
ex:Item rdfs:subClassOf ex:ItemClass .
ex:Item rdfs:subClassOf [
    a owl:Restriction ; owl:onProperty basf:basedOn ;
    owl:onClass [ owl:unionOf ( {base_list} ) ]
] .
ex:Item rdfs:subClassOf [ {r2} ; owl:onClass basf:CoatingLayer ] .
basf:CoatingLayer {union} ( {members} ) .
ex:M rdfs:subClassOf [ {member_restriction} ] .
"""


def b1(r1="a owl:Restriction ; owl:onProperty basf:basedOn ; owl:onClass ex:B",
       r2="a owl:Restriction ; owl:onProperty basf:interactsWith ; "
          "owl:onClass ex:IC", extra=""):
    """An ex:Item for the FIRST union branch, with each restriction a
    parameter."""
    return PREFIXES + f"""
ex:Item rdfs:subClassOf ex:ItemClass .
ex:Item rdfs:subClassOf [ {r1} ] .
ex:Item rdfs:subClassOf [ {r2} ] .
{extra}
"""


SCENARIOS = {
    # found by the second branch only (positive cases)
    "b2-index2": b2(),
    "b2-index0": b2(base_list="ex:IC ex:IC ex:BaseB", members="ex:M"),
    # second branch with one term off: ex:Item must not appear
    "b2-filter-base-layer": b2(base_list="ex:IC"),
    "b2-member-not-restriction": b2(member_restriction=
        "owl:onProperty basf:hasEquivalentCoatingLayer ; owl:someValuesFrom ex:IC"),
    "b2-member-other-property": b2(member_restriction=
        "a owl:Restriction ; owl:onProperty basf:basedOn ; owl:someValuesFrom ex:IC"),
    "b2-member-onclass": b2(member_restriction=
        "a owl:Restriction ; owl:onProperty basf:hasEquivalentCoatingLayer ; "
        "owl:onClass ex:IC"),
    "b2-intersection": b2(union="owl:intersectionOf"),
    "b2-r2-not-restriction": b2(r2="owl:onProperty basf:interactsWith"),
    "b2-r2-other-property": b2(r2="a owl:Restriction ; owl:onProperty basf:otherProperty"),
    # the member of the union reaches its restriction by rdfs:seeAlso
    "b2-member-not-subclass": b2().replace("ex:M rdfs:subClassOf", "ex:M rdfs:seeAlso"),
    # the interactsWith restriction hangs off ex:Item by owl:equivalentClass
    "b2-r2-not-subclass": b2().replace(
        "ex:Item rdfs:subClassOf [ a owl:Restriction ; owl:onProperty basf:interactsWith",
        "ex:Item owl:equivalentClass [ a owl:Restriction ; owl:onProperty basf:interactsWith"),
    # first branch: the positive case, then one term off
    "b1-positive": b1(),
    "b1-coating-layer-interface": b1(r2=
        "a owl:Restriction ; owl:onProperty basf:interactsWith ; "
        "owl:onClass basf:CoatingLayer"),
    "b1-r1-not-restriction": b1(r1="owl:onProperty basf:basedOn ; owl:onClass ex:B"),
    "b1-r2-not-restriction": b1(r2="owl:onProperty basf:interactsWith ; owl:onClass ex:IC"),
    "b1-two-interacts": b1(r1=
        "a owl:Restriction ; owl:onProperty basf:interactsWith ; owl:onClass ex:B"),
    "b1-two-based-on": b1(r2=
        "a owl:Restriction ; owl:onProperty basf:basedOn ; owl:onClass ex:IC"),
    # the basedOn restriction hangs off ex:Item by owl:equivalentClass
    "b1-r1-not-subclass": b1().replace(
        "ex:Item rdfs:subClassOf [ a owl:Restriction ; owl:onProperty basf:basedOn",
        "ex:Item owl:equivalentClass [ a owl:Restriction ; owl:onProperty basf:basedOn"),
    # the interactsWith restriction hangs off ex:Item by owl:equivalentClass
    "b1-r2-not-subclass": b1().replace(
        "ex:Item rdfs:subClassOf [ a owl:Restriction ; owl:onProperty basf:interactsWith",
        "ex:Item owl:equivalentClass [ a owl:Restriction ; owl:onProperty basf:interactsWith"),
    # FILTER(?item != ?item_class): ex:Self is its own only superclass and
    # its own restriction (basedOn and interactsWith), so ?item_class can
    # only be ex:Self
    "top-item-is-item-class": PREFIXES + """
ex:Self rdfs:subClassOf ex:Self ;
    a owl:Restriction ;
    owl:onProperty basf:basedOn , basf:interactsWith ;
    owl:onClass ex:B .
""",
}


class KnowledgeGraph:
    """Stand-in for kglab.KnowledgeGraph, the second graph the repository
    hands run_query (scripts/oxrdf.py:55-57).  query() is
    kglab/query/mixin.py:45-71 (QueryingMixin.query) verbatim, docstring
    aside: keyword-only `bindings`, forwarded as initBindings to the rdflib
    graph it wraps."""

    def __init__(self, graph):
        self._g = graph

    def query (
        self,
        sparql: str,
        *,
        bindings: dict = None,
        ):
        if not bindings:
            bindings = {}

        for row in self._g.query( # type: ignore
                sparql,
                initBindings=bindings,
            ):
            yield row

    def __eq__(self, other):
        return (isinstance(other, KnowledgeGraph)
                and graphs_isomorphic(self._g, other._g))

    def __hash__(self):
        return 0


def kg_call(ttl):
    return lambda: ((KnowledgeGraph(_graph(ttl)),), {})


def drop_addresses(text):
    """drop_nondeterminism, plus the object address in the default repr of
    the KnowledgeGraph stand-in (kglab defines no __repr__)."""
    return re.sub(r" at 0x[0-9a-f]+", " at 0x<addr>", drop_nondeterminism(text))


VERDICT = run_pair(
    __file__,
    entry="run_query",
    calls=[call(RICH_TTL), call(EMPTY_TTL)]
          + [call(ttl) for ttl in SCENARIOS.values()]
          + [kg_call(RICH_TTL), kg_call(SCENARIOS["b2-index2"])],
    stdout_filter=drop_addresses,
)
