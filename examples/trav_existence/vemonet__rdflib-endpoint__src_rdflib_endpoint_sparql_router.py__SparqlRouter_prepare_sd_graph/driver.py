"""Validation driver for vemonet__rdflib-endpoint__src_rdflib_endpoint_sparql_router.py__SparqlRouter_prepare_sd_graph.

Establishes semantic equivalence of original.py and translated.ldpy.

The region is module-level code that imports ``self`` and ``sd_subj`` from
``shim``.  With the generic ``run_pair``, both sides imported the SAME shim
module (one entry in ``sys.modules``), hence the SAME
``self.service_description`` Graph: the translated side ran on a graph the
original had already modified, and the module-state comparison compared that
graph with itself — a translation that added nothing stayed green.  This
driver therefore drops ``shim`` from ``sys.modules`` before each side, imports
it afresh, seeds that side's own graph and ``sd_subj``, and only then
executes the artefact (whose ``from shim import self, sd_subj`` gets the
seeded module).  It asserts that the two sides' graphs are distinct objects
before comparing them by isomorphism.

Each scenario runs both sides once on a fresh graph:

  * ``empty``: nothing in the graph (the case the former generic driver
    meant to run), the guard is true, the triple is added;
  * ``neighbours``: the graph holds the three triples that share two of the
    three terms with the guarded one — ``sd_subj sd:resultFormat
    formats:Turtle`` (other object), ``sd_subj sd:feature formats:RDF_XML``
    (other predicate), ``ex:other sd:resultFormat formats:RDF_XML`` (other
    subject).  None of them must satisfy the guard: a guard widened to a
    variable in any position would see one and skip the add;
  * ``present``: the guarded triple is already there (with the neighbours),
    the guard is false and nothing changes;
  * ``bnode``: ``sd_subj`` is a fresh ``BNode()``, the value the repository
    actually uses when the service description has no ``sd:endpoint`` yet
    (sparql_router.py:418, ``next(...) or BNode()``), and another blank node
    in the graph carries ``sd:resultFormat formats:RDF_XML``.  A blank node
    interpolated into the pattern must stay that one node, not act as a
    SPARQL variable that matches the other blank node;
  * ``bnode_present``: same blank ``sd_subj``, already carrying the triple.

For each scenario the driver also checks, on the original alone, that the
region added exactly the number of triples the scenario is built for (1, or
0 for the ``*present`` ones): the scenario provably reaches its branch.
"""
import sys
import traceback
from pathlib import Path

from rdflib import BNode, Graph, Namespace, URIRef

from rdfeval import harness

ex_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(ex_dir))

SD = Namespace("http://www.w3.org/ns/sparql-service-description#")
FORMATS = Namespace("http://www.w3.org/ns/formats/")
SUBJ = URIRef("http://example.org/sparql")
OTHER = URIRef("http://example.org/other")


def _neighbours(g, s):
    g.add((s, SD.resultFormat, FORMATS.Turtle))
    g.add((s, SD.feature, FORMATS.RDF_XML))
    g.add((OTHER, SD.resultFormat, FORMATS.RDF_XML))


def scenario_empty():
    return Graph(), SUBJ


def scenario_neighbours():
    g = Graph()
    _neighbours(g, SUBJ)
    return g, SUBJ


def scenario_present():
    g, s = scenario_neighbours()
    g.add((s, SD.resultFormat, FORMATS.RDF_XML))
    return g, s


def scenario_bnode():
    g, s = Graph(), BNode()
    _neighbours(g, s)
    g.add((BNode(), SD.resultFormat, FORMATS.RDF_XML))
    return g, s


def scenario_bnode_present():
    g, s = scenario_bnode()
    g.add((s, SD.resultFormat, FORMATS.RDF_XML))
    return g, s


SCENARIOS = [scenario_empty, scenario_neighbours, scenario_present,
             scenario_bnode, scenario_bnode_present]


def _load(filename, name, scenario):
    """Execute one side on its own, freshly imported and seeded shim."""
    sys.modules.pop("shim", None)
    import shim
    shim.self.service_description, shim.sd_subj = scenario()
    before = len(shim.self.service_description)
    ns, out = harness._exec_artefact(ex_dir / filename, name)
    return ns, out, before


verdict: dict = {"example": ex_dir.name, "equivalent": False,
                 "method": "module-state per scenario (separate shim per side)",
                 "diffs": [], "error": None}
try:
    left, right = harness.sides_from_env()
    verdict["sides"] = [left, right]
    diffs: list = []
    for scenario in SCENARIOS:
        label = scenario.__name__
        ns_o, out_o, before_o = _load(left, "__original__", scenario)
        ns_t, out_t, _ = _load(right, "__translated__", scenario)
        go, gt = ns_o["service_description"], ns_t["service_description"]
        if go is gt:
            diffs.append(f"{label}: both sides share one graph (hollow comparison)")
        harness._compare_value(go, gt, f"{label}: service_description", diffs)
        added = len(go) - before_o
        expected = 0 if label.endswith("present") else 1
        if added != expected:
            diffs.append(f"{label}: original added {added} triple(s), "
                         f"scenario expects {expected}")
        if out_o != out_t:
            diffs.append(f"{label}: stdout differs")
    sys.modules.pop("shim", None)
    verdict["calls"] = len(SCENARIOS)
    verdict["observed"] = True
    verdict["diffs"] = diffs
    verdict["equivalent"] = not diffs
except Exception:
    verdict["error"] = traceback.format_exc(limit=8)

harness._emit(verdict)
VERDICT = verdict
