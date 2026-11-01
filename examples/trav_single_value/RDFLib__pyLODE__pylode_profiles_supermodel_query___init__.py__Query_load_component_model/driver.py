"""Driver for Query.load_component_model (pyLODE), trav_single_value.

The line under study is `order = db.value(iri, SH.order)`, a "first value
or None" read through a Dataset (pylode's own `Dataset(default_union=True)`
subclass, as the real loader builds it), followed by
`int(order) if order is not None else None` -- so the value it reads decides
`ComponentModel.order` (and a missing one becomes the model's default).

Everything else is the real package: `self` is a real `Query` (built with
`Query.__new__` and the four attributes the region's callees read, because
`Query.__init__` fetches profiles over HTTP), and the callees are the real
`get_name`, `get_descriptions`, `get_rdf_properties`, ... of pylode 3.2.3.

Cases (the fixture is the content of the named graph of profile A):

  A  ex:profile/a            one sh:order (2) in its own graph; neighbours:
                             profile B's order (9), the work example's
                             order (0), sh:name, and ex:order (99)
  B  ex:profile/c            a named graph with no sh:order at all: the
                             value is None although other subjects, in
                             other graphs of the union, have one
  C  ex:profile/d            its sh:order (5) lives in ANOTHER named graph
                             (the config graph): found through the union
  D  ex:profile/e            a typed order, "7"^^xsd:integer, in its graph
  E  ex:profile/f            a non-numeric order: int() raises, on both sides
  F  ex:profile/a, a Dataset WITHOUT default_union: the default graph is
                             empty, so the order is None
"""
from rdflib import Graph, Literal, URIRef
from rdflib.namespace import RDFS, SH, XSD

from pylode.profiles.supermodel.dataset import Dataset
from pylode.profiles.supermodel.query import Query

from rdfeval.harness import fixture_graph, run_pair

from pathlib import Path

HERE = Path(__file__).resolve().parent
P = "http://example.org/profile/"
CONFIG = URIRef("urn:graph:pylode-config")


def _named(db, iri, *triples):
    g = Graph(identifier=URIRef(iri))
    for t in triples:
        g.add(t)
    db.add_graph(g)


def _self(db, root):
    q = Query.__new__(Query)
    q.db = db
    q.class_index = set()
    q.profiles_order = []
    q.root_profile_iri = URIRef(root)
    return q


def _db(default_union=True):
    db = Dataset(default_union=default_union)
    db.add_graph(Graph(identifier=CONFIG))
    return db


def _profile_a(db):
    g = Graph(identifier=URIRef(P + "a"))
    g += fixture_graph(HERE / "fixture.ttl")
    db.add_graph(g)


def case_a():
    db = _db()
    _profile_a(db)
    return ((_self(db, P + "a"), URIRef(P + "a"), db), {})


def case_b():
    db = _db()
    _profile_a(db)
    _named(db, P + "c", (URIRef(P + "c"), RDFS.label, Literal("Profile C")))
    return ((_self(db, P + "a"), URIRef(P + "c"), db), {})


def case_c():
    db = _db()
    _named(db, P + "d", (URIRef(P + "d"), RDFS.label, Literal("Profile D")))
    db.add((URIRef(P + "d"), SH.order, Literal(5), CONFIG))
    return ((_self(db, P + "d"), URIRef(P + "d"), db), {})


def case_d():
    db = _db()
    _named(db, P + "e", (URIRef(P + "e"), RDFS.label, Literal("Profile E")),
           (URIRef(P + "e"), SH.order, Literal("7", datatype=XSD.integer)))
    return ((_self(db, P + "e"), URIRef(P + "e"), db), {})


def case_e():
    db = _db()
    _named(db, P + "f", (URIRef(P + "f"), RDFS.label, Literal("Profile F")),
           (URIRef(P + "f"), SH.order, Literal("first")))
    return ((_self(db, P + "f"), URIRef(P + "f"), db), {})


def case_f():
    db = _db(default_union=False)
    _profile_a(db)
    return ((_self(db, P + "a"), URIRef(P + "a"), db), {})


VERDICT = run_pair(
    __file__,
    entry="load_component_model",
    calls=[case_a, case_b, case_c, case_d, case_e, case_f],
)
