"""Validation driver for Display-Lab__scaffold__src_candidate_pudding_candidate_pudding.py__create_candidate.

The region takes two rdflib Resources and works on the graph behind them
(`measure.graph`), and returns either None or the candidate Resource.  The
harness cannot compare an rdflib Resource (`Resource.__iter__` yields (s, p, o)
triples of Resources, subject included, so `harness.materialise` recurses on it
forever), hence a hand-written driver: it passes real `Resource`s, as the
repository does, runs each case on both sides, and compares

  * the exception raised, if any (type and message);
  * both graphs by isomorphism after the call (the partial one if it raised);
  * a description of the returned value: None, or a Resource whose graph is
    the measure's graph and whose identifier is a blank node with the type
    triple `slowmo:Candidate` in that graph.

Cases (each one the neighbourhood the region reads, with falsy and
non-matching neighbours):

  * `no_pathway`            no cpo:has_causal_pathway: returns None before
                            writing anything;
  * `falsy_pathway`         the pathway value is `Literal(0)`, which is falsy:
                            the guard `not template.value(...)` is on the
                            truthiness of the value, not on its presence;
  * `no_pathway_but_motivating` / `falsy_pathway_but_motivating`  the same two
                            guards with a motivating information that WOULD
                            be accepted, so a guard that lets the template
                            through (`is None` instead of falsy, or no guard)
                            gives a different graph and return value;
  * `nothing_motivating`    pathway present, no motivating information regards
                            the measure: the candidate is created, typed, then
                            removed; the graph must come out untouched.  This
                            is the path the `remove` stratum is about;
  * `prior_candidate`       same, but the graph already holds an earlier
                            candidate with the SAME type, measure and template:
                            the removal must take only the new blank node's
                            triples (an earlier one, or every triple that
                            shares a term with it, must stay);
  * `accepted`              a motivating information regards the measure (and
                            one regards another measure): the candidate is
                            kept and returned, and the graph shows the three
                            triples the region writes (`rdf:type`,
                            `slowmo:RegardingMeasure`, `slowmo:AncestorTemplate`)
                            plus what the two helpers add;
  * `accepted_two_templates` the same, with a second template that has a
                            different name: the ancestor template is the one
                            passed, not a neighbour;
  * `accepted_incomplete_template`  a template without the text property: the
                            helper `add_convenience_properties` raises
                            (AssertionError) after the region wrote its
                            three triples, and the partial graph and the
                            exception are compared;
  * `separate_graphs`       the template lives in another graph than the
                            measure: the candidate is written to, and removed
                            from, the measure's graph only;
  * `separate_graphs_accepted`  the same with a motivating information, which
                            reaches the helper `add_convenience_properties`
                            on a template whose triples are not in the
                            measure's graph (whatever that does is compared,
                            raise included).
"""
import traceback
from pathlib import Path

from rdflib import BNode, Graph, Literal, URIRef
from rdflib.namespace import RDF
from rdflib.resource import Resource

from rdfeval.harness import _emit, _exec_artefact, graphs_isomorphic, sides_from_env
from scaffold_context import CPO, DEFAULT_DISPLAY, IAO, PSDO, SCHEMA, SLOWMO

HERE = Path(__file__).resolve().parent

MEASURE = URIRef("http://example.org/measure/PONV05")
OTHER_MEASURE = URIRef("http://example.org/measure/BP01")
TEMPLATE = URIRef("http://example.org/template/social-comparison")
OTHER_TEMPLATE = URIRef("http://example.org/template/top-performer")
PATHWAY = URIRef("http://example.org/pathway/social-better")


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


TEXT = URIRef("https://schema.metadatacenter.org/properties/"
              "6b9dfdf9-9c8a-4d85-8684-a24bee4b85a8")


def _with_template(g: Graph, template, name, complete=True):
    """A template the two helpers can read to the end (name, text, display,
    comparator); `complete=False` leaves out the text, which makes
    `add_convenience_properties` raise AFTER the region wrote its triples."""
    g.add((template, SCHEMA.name, Literal(name)))
    g.add((template, CPO.has_causal_pathway, PATHWAY))
    g.add((template, IAO.is_about, MEASURE))
    if complete:
        g.add((template, TEXT, Literal("text of " + name)))
        g.add((template, DEFAULT_DISPLAY, Literal("display of " + name)))


def _regarding_measure(g: Graph) -> None:
    g.add((BNode("performance_content"), PSDO.motivating_information,
           BNode("mi2")))
    g.add((BNode("mi2"), SLOWMO.RegardingMeasure, MEASURE))


def no_pathway():
    g = _base_graph()
    return g, g, g.resource(MEASURE), g.resource(TEMPLATE)


def falsy_pathway():
    g = _base_graph()
    g.add((TEMPLATE, CPO.has_causal_pathway, Literal(0)))
    return g, g, g.resource(MEASURE), g.resource(TEMPLATE)


def no_pathway_but_motivating():
    g = _base_graph()
    _regarding_measure(g)
    g.remove((TEMPLATE, CPO.has_causal_pathway, None))
    return g, g, g.resource(MEASURE), g.resource(TEMPLATE)


def falsy_pathway_but_motivating():
    g = _base_graph()
    _regarding_measure(g)
    g.add((TEMPLATE, CPO.has_causal_pathway, Literal(0)))
    return g, g, g.resource(MEASURE), g.resource(TEMPLATE)


def nothing_motivating():
    g = _base_graph()
    g.add((TEMPLATE, CPO.has_causal_pathway, PATHWAY))
    return g, g, g.resource(MEASURE), g.resource(TEMPLATE)


def prior_candidate():
    g = _base_graph()
    g.add((TEMPLATE, CPO.has_causal_pathway, PATHWAY))
    old = BNode("old_candidate")
    g.add((old, RDF.type, SLOWMO.Candidate))
    g.add((old, SLOWMO.RegardingMeasure, MEASURE))
    g.add((old, SLOWMO.AncestorTemplate, TEMPLATE))
    return g, g, g.resource(MEASURE), g.resource(TEMPLATE)


def accepted():
    g = _base_graph()
    _with_template(g, TEMPLATE, "Social comparison")
    _regarding_measure(g)
    return g, g, g.resource(MEASURE), g.resource(TEMPLATE)


def accepted_two_templates():
    g = _base_graph()
    _with_template(g, TEMPLATE, "Social comparison")
    _with_template(g, OTHER_TEMPLATE, "Top performer")
    _regarding_measure(g)
    return g, g, g.resource(MEASURE), g.resource(OTHER_TEMPLATE)


def accepted_incomplete_template():
    g = _base_graph()
    _with_template(g, TEMPLATE, "Social comparison", complete=False)
    _regarding_measure(g)
    return g, g, g.resource(MEASURE), g.resource(TEMPLATE)


def separate_graphs():
    g = _base_graph()
    t = Graph()
    _with_template(t, TEMPLATE, "Social comparison")
    return g, t, g.resource(MEASURE), t.resource(TEMPLATE)


def separate_graphs_accepted():
    g = _base_graph()
    _regarding_measure(g)
    t = Graph()
    _with_template(t, TEMPLATE, "Social comparison")
    return g, t, g.resource(MEASURE), t.resource(TEMPLATE)


CASES = [no_pathway, falsy_pathway, no_pathway_but_motivating,
         falsy_pathway_but_motivating, nothing_motivating, prior_candidate,
         accepted, accepted_two_templates, accepted_incomplete_template,
         separate_graphs,
         separate_graphs_accepted]


def _describe(result, graph):
    """A comparable description of the returned Resource (or None)."""
    if result is None:
        return None
    return ("resource",
            isinstance(result, Resource),
            result.graph is graph,
            type(result.identifier).__name__,
            (result.identifier, RDF.type, SLOWMO.Candidate) in graph)


def _call(fn, case):
    g, t, measure, template = case()
    try:
        outcome = _describe(fn(measure, template), g)
    except Exception as e:                       # noqa: BLE001 - compared
        outcome = ("raised", type(e).__name__, str(e))
    return outcome, g, t


verdict = {"example": HERE.name, "equivalent": False,
           "method": "entry:create_candidate (hand-written: Resource return "
                     "described, graphs by isomorphism)",
           "diffs": [], "error": None}

try:
    left, right = sides_from_env()
    verdict["sides"] = [left, right]
    ns_o, _ = _exec_artefact(HERE / left, "__original__")
    ns_t, _ = _exec_artefact(HERE / right, "__translated__")
    fo, ft = ns_o["create_candidate"], ns_t["create_candidate"]

    diffs: list[str] = []
    for case in CASES:
        out_o, g_o, t_o = _call(fo, case)
        out_t, g_t, t_t = _call(ft, case)
        if out_o != out_t:
            diffs.append(f"{case.__name__}: outcome {out_o!r} vs {out_t!r}")
        if not graphs_isomorphic(g_o, g_t):
            diffs.append(f"{case.__name__}: measure graph not isomorphic "
                         f"({len(g_o)} vs {len(g_t)} triples)")
        if t_o is not g_o and not graphs_isomorphic(t_o, t_t):
            diffs.append(f"{case.__name__}: template graph not isomorphic "
                         f"({len(t_o)} vs {len(t_t)} triples)")
    verdict["calls"] = len(CASES)
    verdict["observed"] = True
    verdict["diffs"] = diffs
    verdict["equivalent"] = not diffs
except Exception:
    verdict["error"] = traceback.format_exc(limit=8)

_emit(verdict)
