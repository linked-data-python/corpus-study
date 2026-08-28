"""Validation driver: Class.__repr__ renders a class as Manchester syntax.

The region is extracted as a free function still taking ``self``, so the
fixtures build real infixowl Class objects (from the same shim both sides
import) over small OWL graphs and the harness compares the returned string.
Fixtures cover the four rendering paths the region branches on: subClassOf,
equivalentClass, disjointWith/complementOf, and the owl:unionOf lookup done
by triples_choices.  Every fixture class is named (no BNode identifiers), so
the rendered text is deterministic and the two runs are comparable.
"""
from rdflib import Graph, Literal, Namespace, OWL, RDFS

from infixowl_shim import BooleanClass, Class
from rdfeval.harness import run_pair

EX = Namespace("http://example.com/")


def _graph():
    g = Graph()
    g.bind("ex", EX, override=False)
    return g


def primitive_class():
    g = _graph()
    a = Class(EX.Opera, graph=g)
    a.subClassOf = [Class(EX.MusicalWork, graph=g), Class(EX.Work, graph=g)]
    g.add((EX.Opera, RDFS.label, Literal("Opera")))
    g.add((EX.Opera, RDFS.comment, Literal("A dramatic work set to music")))
    return ((a,), {})


def primitive_class_full():
    (a,), _ = primitive_class()
    return ((a,), {"full": True})


def defined_class():
    g = _graph()
    a = Class(EX.Woman, graph=g)
    a.equivalentClass = [Class(EX.FemaleHuman, graph=g)]
    a.disjointWith = [Class(EX.Man, graph=g)]
    g.add((EX.Woman, RDFS.label, Literal("Woman")))
    return ((a,), {})


def union_class():
    g = _graph()
    members = [Class(EX.Africa, graph=g), Class(EX.NorthAmerica, graph=g)]
    a = BooleanClass(EX.Continent, operator=OWL.unionOf, members=members,
                     graph=g)
    return ((a,), {})


VERDICT = run_pair(__file__, entry="__repr__",
                   calls=[primitive_class, primitive_class_full,
                          defined_class, union_class])
