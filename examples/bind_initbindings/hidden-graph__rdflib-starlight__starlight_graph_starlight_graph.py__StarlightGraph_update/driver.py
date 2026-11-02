"""Validation driver for hidden-graph__rdflib-starlight__starlight_graph_starlight_graph.py__StarlightGraph_update.

`update` is a method of StarlightGraph (a package that is not on PyPI), so
`self` is a stub: an rdflib Graph subclass loaded from fixture.ttl, with
`_is_native = False` and a `_build_registry_from_store` that prints, so that
stdout shows the method reached its last line.  The update is passed as an
already-prepared Update object (the `str` branch needs the package
sparql1_2_to_rdf, absent from the study venv).

Calls (each re-parses the fixture):
  * INSERT .. WHERE over the sensors, no initBindings: s1 and s2 get the
    triple, ex:o1 does not;
  * the same update with initBindings {s: ex:s1}: only s1;
  * a DELETE .. WHERE that names ex:Sensor with the status "ok": both
    sensors lose it, ex:o1 keeps it;
  * an update that matches nothing (ex:Missing): the graph is unchanged;
  * a graph that already has its own prefix binding (kept on the raw view).
The graph itself is the argument compared after each call (mutation).
"""
from pathlib import Path

from rdflib import Graph, Literal, URIRef
from rdflib.plugins.sparql import prepareUpdate

from rdfeval.harness import run_pair

FIXTURE = Path(__file__).resolve().parent / "fixture.ttl"
EX = "http://example.org/"
PFX = f"PREFIX ex: <{EX}>\n"


class _StarlightStub(Graph):
    _is_native = False

    def _build_registry_from_store(self):
        print("registry rebuilt", len(self))


def _graph(bind=None):
    g = _StarlightStub()
    g.parse(FIXTURE, format="turtle")
    if bind:
        g.bind(*bind)
    return g


def call(update, bind=None, **kw):
    def _make():
        return (_graph(bind), prepareUpdate(PFX + update)), dict(kw)
    return _make


INSERT = "INSERT { ?s ex:seen true } WHERE { ?s a ex:Sensor }"
DELETE = 'DELETE { ?s ex:status "ok" } WHERE { ?s a ex:Sensor ; ex:status "ok" }'
NOTHING = "INSERT { ?s ex:seen true } WHERE { ?s a ex:Missing }"

VERDICT = run_pair(
    __file__,
    entry='update',
    calls=[
        call(INSERT),
        call(INSERT, initBindings={"s": URIRef(EX + "s1")}),
        call(DELETE),
        call(NOTHING),
        call(INSERT, bind=("shared", EX), processor="sparql", use_store_provided=False),
    ],
)
