"""Validation driver for johnjung__metadata_converters__test_soc_sci_maps_marcxml_to_edm.py__TestSocSciMapsMarcXmlToEDM_test_cho_language.

The region is a unittest.TestCase method: it asserts that
`g.value(subject=cho, predicate=dc:language) == Literal('en')` and returns
None.  `demo(self)` (identical on both sides, see original.py) turns the
outcome into a value: "ok", or ("assertion-failed", message) where the message
of assertEqual shows the value that was read, so a wrong read is visible, not
just a failed test.  `_Case` supplies what the real class's setUp binds:
`edm[ids].graph` (an rdflib Graph) and `cho[ids]` (the object's IRI).

Calls (each on a fresh graph; the fixture is fixture.ttl, edited in memory):
  fixture      "en" is there: ok; neighbours with "fr", dcterms:language,
               ex:language must not interfere
  other_value  dc:language is "fr": assertion-failed, message shows 'fr'
  none         no dc:language on the object: None != Literal('en')
  two_en_fr    two values, "en" then "fr"; the first one read is compared
  two_fr_en    two values, "fr" then "en": the other order
  lang_tag     "en"@en: not equal to Literal('en')
  typed        "en"^^xsd:string: not equal to Literal('en') either
  iri_value    the value is an IRI
  wrong_cho    self.cho[ids] names an object whose language is "fr"
  other_ids    self.cho maps the ids to the neighbour with only dcterms
  missing_ids  self.edm has no entry for ids: KeyError (a raise is compared)
  empty        an empty graph
"""
import unittest
from pathlib import Path
from types import SimpleNamespace

from rdflib import Graph, Literal, Namespace, URIRef, XSD

from rdfeval.harness import fixture_graph, run_pair

HERE = Path(__file__).resolve().parent
FIXTURE = HERE / "fixture.ttl"
IDS = "7641168,3451312"
CHO = URIRef("http://example.org/cho/" + IDS)
DC = Namespace("http://purl.org/dc/elements/1.1/")


class _Case(unittest.TestCase):
    """Stand-in for TestSocSciMapsMarcXmlToEDM: `.edm`, `.cho`, assertEqual."""

    def __init__(self, graph, cho=CHO, edm_key=IDS):
        super().__init__("runTest")
        self.edm = {edm_key: SimpleNamespace(graph=graph)}
        self.cho = {IDS: cho}

    def runTest(self):
        pass


def call(edit=None, cho=CHO, edm_key=IDS, empty=False):
    def c():
        g = Graph() if empty else fixture_graph(FIXTURE)
        if edit:
            edit(g)
        return ((_Case(g, cho, edm_key),), {})
    return c


def replacing(*values):
    """Replace the dc:language of the object by `values`, in that order."""
    def edit(g):
        g.remove((CHO, DC.language, None))
        for v in values:
            g.add((CHO, DC.language, v))
    return edit


VERDICT = run_pair(
    __file__,
    entry="demo",
    calls=[
        call(),
        call(replacing(Literal("fr"))),
        call(lambda g: g.remove((CHO, DC.language, None))),
        call(replacing(Literal("en"), Literal("fr"))),
        call(replacing(Literal("fr"), Literal("en"))),
        call(replacing(Literal("en", lang="en"))),
        call(replacing(Literal("en", datatype=XSD.string))),
        call(replacing(URIRef("http://example.org/lang/en"))),
        call(cho=URIRef("http://example.org/cho/1111111")),
        call(cho=URIRef("http://example.org/cho/2222222")),
        call(edm_key="other"),
        call(empty=True),
    ],
)
