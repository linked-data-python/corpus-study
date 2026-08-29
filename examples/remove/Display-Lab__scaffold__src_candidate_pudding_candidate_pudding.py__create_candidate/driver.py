"""Validation driver for Display-Lab__scaffold__src_candidate_pudding_candidate_pudding.py__create_candidate.

The region takes two rdflib Resources and works on the graph behind them
(`measure.graph`), so the oracle is the isomorphism of that graph after the
call — plus the value returned.

Two calls, the two paths that reach a `return None`:

  * `no_pathway`  — the template carries no cpo:has_causal_pathway, the region
    returns before writing anything: the graph must come out untouched;
  * `nothing_motivating` — the template has a causal pathway, so a candidate is
    created and typed, but no motivating information regards the measure: the
    region removes the candidate again, and the graph must come out untouched
    all the same.  This is the path the `remove` stratum is about.

The third path returns the candidate itself, and the harness cannot compare an
rdflib Resource: `Resource.__iter__` yields (s, p, o) triples of Resources,
subject included, so `harness.materialise` recurses on it forever.  That is why
the two arguments are `GraphProbe`s below, and why the accepted-candidate path
is left out (see meta.json).
"""
from rdflib import BNode, Graph, Literal, URIRef
from rdflib.namespace import RDF
from rdflib.resource import Resource

from rdfeval.harness import run_pair
from scaffold_context import CPO, PSDO, SCHEMA, SLOWMO

MEASURE = URIRef("http://example.org/measure/PONV05")
OTHER_MEASURE = URIRef("http://example.org/measure/BP01")
TEMPLATE = URIRef("http://example.org/template/social-comparison")
PATHWAY = URIRef("http://example.org/pathway/social-better")


class GraphProbe(Resource):
    """A Resource whose comparison key is the whole graph behind it.

    The region mutates `measure.graph`, and that graph is what the isomorphism
    oracle must see; iterating an rdflib Resource cannot be walked by
    `harness.materialise` (it recurses through the subject).  Only iteration is
    overridden, so every comparison the region itself performs stays rdflib's.
    """

    def __iter__(self):
        return iter((self._graph,))


def _base_graph() -> Graph:
    """A performance content node, one motivating information about *another*
    measure, and a named template — the neighbourhood the region reads."""
    g = Graph()
    performance_content = BNode("performance_content")
    motivating_information = BNode("mi1")
    g.add((MEASURE, RDF.type, PSDO.comparator_content))
    g.add((performance_content, PSDO.motivating_information,
           motivating_information))
    g.add((motivating_information, SLOWMO.RegardingMeasure, OTHER_MEASURE))
    g.add((TEMPLATE, SCHEMA.name, Literal("Social comparison")))
    return g


def no_pathway():
    g = _base_graph()
    return ((GraphProbe(g, MEASURE), GraphProbe(g, TEMPLATE)), {})


def nothing_motivating():
    g = _base_graph()
    g.add((TEMPLATE, CPO.has_causal_pathway, PATHWAY))
    return ((GraphProbe(g, MEASURE), GraphProbe(g, TEMPLATE)), {})


VERDICT = run_pair(
    __file__,
    entry='create_candidate',
    calls=[no_pathway, nothing_motivating],
)
