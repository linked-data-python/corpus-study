"""Validation driver for tetherless-world__materialsmine__tests_test_chem_props_ingest.py__ChemPropsTest_no_test_material.

The region is a unittest.TestCase method: it only asserts and returns None,
and the two `objects()` traversals it contains feed lists that are then
discarded by `.sort()` (which returns None).  A plain call would therefore
show nothing about those reads.  Two things make the original show them:

  * `self.app.db` is a `ReadLog` graph: a real rdflib Graph whose `triples()`
    records every pattern asked and every triple yielded.  `objects()` (the
    original) and `m{ }` (the translation) both read through it, so the
    multiset of (pattern, triple) the two sides read is part of the value.
  * `demo(self)` (identical on both sides, see original.py) returns
    ("ok" | ("assertion-failed", msg), sorted reads), turning a failed
    assertion into a comparable value.

Calls (each builds a fresh `_Case` over a fresh graph):
  full         fixture.ttl as is: the query finds exactly the three expected
               materials -> "ok"; altLabel/notation are read for each of them,
               never for the neighbours (a non-chemical, a chemical without
               density, prefLabel/hiddenLabel, a density node that carries an
               altLabel).
  extra_label  fixture + a fourth chemical: the query finds one material more
               than expected -> assertion-failed, and a fourth altLabel read.
  no_label     one expected chemical loses its rdfs:label: the query yields
               two rows -> assertion-failed (zero-solution row for that one).
  empty        an empty graph: no row, no read at all -> assertion-failed.
  two_dens     one chemical with two density attributes: the query yields a
               row per (chem, den) -> assertion-failed, altLabel read twice.
  altlabel_iri an altLabel whose value is an IRI and one that is a typed
               integer, to see terms go through unchanged.
"""
import unittest
from pathlib import Path
from types import SimpleNamespace

from rdflib import Graph

from rdfeval.harness import fixture_graph, run_pair

HERE = Path(__file__).resolve().parent
FIXTURE = HERE / "fixture.ttl"

PRE = """
@prefix sio: <http://semanticscience.org/resource/> .
@prefix dcterms: <http://purl.org/dc/terms/> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix ex: <http://example.org/> .
"""


class ReadLog(Graph):
    """A Graph that remembers each pattern asked of `triples()` and each
    triple it yielded (the `objects()` of rdflib and the `m{ }` island both
    come down to `triples()`)."""

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self.reads = []

    def triples(self, triple):
        self.reads.append(("ask", tuple(triple)))
        for t in super().triples(triple):
            self.reads.append(("got", tuple(triple), t))
            yield t


class _Case(unittest.TestCase):
    def __init__(self, db):
        super().__init__("runTest")
        self.app = SimpleNamespace(db=db)

    def runTest(self):
        pass


def _db(extra=None, drop=None, empty=False):
    g = ReadLog()
    if not empty:
        g.parse(source=str(FIXTURE), format="turtle")
    if drop:
        for t in drop:
            g.remove(t)
    if extra:
        g.parse(data=PRE + extra, format="turtle")
    g.reads.clear()
    return g


def _call(**kw):
    def call():
        return ((_Case(_db(**kw)),), {})
    return call


def _drop_label():
    from rdflib import Literal, URIRef
    return [(URIRef("http://example.org/ps"),
             URIRef("http://www.w3.org/2000/01/rdf-schema#label"),
             Literal("Polystyrene"))]


EXTRA = """
ex:fourth a sio:ChemicalSubstance ; dcterms:identifier "ZZ" ; rdfs:label "Fourth" ;
    sio:hasAttribute ex:fourth_d ; skos:altLabel "extra alt" ; skos:notation "Z" .
ex:fourth_d sio:hasValue 2.0e0 .
"""
TWO_DENS = """
ex:peek sio:hasAttribute ex:peek_density2 .
ex:peek_density2 sio:hasValue 1.29e0 .
"""
ODD = """
ex:ps skos:altLabel ex:SomeIri, 42, "x"^^xsd:token ;
    skos:notation ex:NotationIri .
"""

VERDICT = run_pair(
    __file__,
    entry="demo",
    calls=[_call(), _call(extra=EXTRA), _call(drop=_drop_label()),
           _call(empty=True), _call(extra=TWO_DENS), _call(extra=ODD)],
)
