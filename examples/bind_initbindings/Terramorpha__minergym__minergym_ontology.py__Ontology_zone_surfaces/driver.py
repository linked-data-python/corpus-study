"""Validation driver for Terramorpha__minergym__minergym_ontology.py__Ontology_zone_surfaces.

Establishes semantic equivalence of original.py and translated.ldpy.

`zone_surfaces` is a method extracted as a free function that takes `self`
explicitly (rdf_ops: 0 -- the region only reads, never adds): its rdflib
graph lives on `self.rdf`, an attribute rather than a module-level name, so
the binding is restored here as a small object the driver builds, not as a
shim module (see minergym/ontology.py: `Ontology` is a dataclass with an
`rdf: rdflib.Graph` field, and `IDF = Namespace("https://energyplus.net/")`
is bound as "idf" on that graph in `Ontology.from_object`, which is why the
raw query string can use `idf:zone_name` with no PREFIX line of its own --
rdflib defaults `initNs` to the graph's own bound namespaces).

The tirage tagged this region `oracle: isomorphism`, but the function only
reads and returns a `list[Node]`; it never builds or mutates a graph, so
isomorphism has nothing to compare (see LA3D trav_existence precedent for
the same mismatch). The real oracle is the reading one: same input graph,
same values out. Three zones exercise it: "z1" has two matching surfaces,
"z2" has exactly one, and "zzz" is absent (the zero-solution case). The
graph also carries neighbourhood that must NOT match: a surface with no
idf:zone_name at all, and a non-surface individual that does carry
idf:zone_name "z1" (a query whose `a "BuildingSurface:Detailed"` pattern
leaked would pick it up).
"""
from types import SimpleNamespace

from rdflib import RDF, Graph, Literal, Namespace

from rdfeval.harness import run_pair

IDF = Namespace("https://energyplus.net/")


def _ontology():
    g = Graph()
    g.bind("idf", IDF)
    g.add((Literal("s1"), RDF.type, Literal("BuildingSurface:Detailed")))
    g.add((Literal("s1"), IDF.zone_name, Literal("z1")))
    g.add((Literal("s2"), RDF.type, Literal("BuildingSurface:Detailed")))
    g.add((Literal("s2"), IDF.zone_name, Literal("z1")))
    g.add((Literal("s3"), RDF.type, Literal("BuildingSurface:Detailed")))
    g.add((Literal("s3"), IDF.zone_name, Literal("z2")))
    # neighbourhood that must not match
    g.add((Literal("s4"), RDF.type, Literal("BuildingSurface:Detailed")))
    g.add((Literal("zoneish"), IDF.zone_name, Literal("z1")))
    return SimpleNamespace(rdf=g)


def _case(zone: str):
    # Built once and shared by both sides: the region only reads, so there
    # is no risk a side mutates the fixture out from under the other, and
    # `run_pair` also compares each argument after the call to catch such
    # mutation -- comparing a fresh SimpleNamespace-wrapping-a-Graph per side
    # would spuriously "differ" since neither SimpleNamespace nor Graph
    # define content equality, only identity.
    obj = _ontology()
    return lambda: ((obj, Literal(zone)), {})


VERDICT = run_pair(
    __file__,
    entry="zone_surfaces",
    calls=[
        _case("z1"),    # 2 solutions
        _case("z2"),    # 1 solution
        _case("zzz"),   # 0 solutions
    ],
)
