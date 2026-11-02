"""Driver for tetherless-world__materialsmine__tests_ingest_tester.py__test_melt_viscosity.

Two facts about the source decide the driver.

* The region is decorated with `@disable_test`: as the source applies it, the
  test is replaced by a function that only prints, and its SPARQL never runs.
  The context shim (ingest_shim.py) keeps the decorator line for line and adds
  a switch, `EXERCISE_BODY`, that makes it hand the test back; set here, so
  that both sides observe the body.
* The body is a test: its whole effect is `runner.assertCountEqual` (and a
  print), so each call shows an outcome — None, or the AssertionError /
  TypeError / KeyError it raises, compared like a value.  A latent bug of the
  source is kept: with `expected_value=None` the code assigns
  `expected_authors` instead of `expected_value`, so the assertion then gets
  None and raises TypeError.

The graph is the `runner.app.db` of the source (a Whyis graph).  The query
joins three triples around the node `bnode:cfff...` of sample ..._9:

  full          two values, the type and the sample link: [1.5, 2.5] found.
  wrong_expected  the same graph, another expectation: AssertionError.
  duplicate     the same value reached twice is still one triple: one value.
  no_type       the type triple missing (the node is not a MeltVisocsity):
                zero solution; expecting [] passes, expecting values fails.
  no_link       the sample does not point to the node: zero solution.
  other_sample  another sample points to the node, not the one of the query.
  none_expected expected_value=None, expected_data holds the key: TypeError.
  none_no_data  expected_value=None, expected_data empty: KeyError.
Neighbours that must not match (another node's values, another predicate on
the node) sit in the graph of every case.
"""
import ingest_shim
ingest_shim.EXERCISE_BODY = True

from rdflib import Graph, Literal, URIRef  # noqa: E402

from rdfeval.harness import run_pair  # noqa: E402
from ingest_shim import Runner  # noqa: E402

NODE = URIRef("bnode:cfff5d04317445c49f22102e124ab68e")
OTHER = URIRef("bnode:0123456789abcdef0123456789abcdef")
SAMPLE = URIRef("http://nanomine.org/sample/l256-s3-potschke-2004_nanomine-meltviscosity_9")
SAMPLE2 = URIRef("http://nanomine.org/sample/other-sample_1")
HAS_VALUE = URIRef("http://semanticscience.org/resource/hasValue")
HAS_ATTR = URIRef("http://semanticscience.org/resource/hasAttribute")
HAS_UNIT = URIRef("http://semanticscience.org/resource/hasUnit")
TYPE = URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type")
MELT = URIRef("http://nanomine.org/ns/MeltVisocsity")
OTHER_CLASS = URIRef("http://nanomine.org/ns/TensileModulus")


def _runner(type_=True, link=True, link_sample=SAMPLE, values=(1.5, 2.5),
            expected_data=None):
    def make():
        g = Graph()
        for v in values:
            g.add((NODE, HAS_VALUE, Literal(v)))
        if type_:
            g.add((NODE, TYPE, MELT))
        if link:
            g.add((link_sample, HAS_ATTR, NODE))
        # neighbours that must not match
        g.add((NODE, HAS_UNIT, Literal("Pa.s")))
        g.add((OTHER, HAS_VALUE, Literal(99.0)))
        g.add((OTHER, TYPE, MELT))
        g.add((SAMPLE, HAS_ATTR, OTHER))
        g.add((SAMPLE2, HAS_ATTR, OTHER))
        return Runner(g, expected_data), 
    return make


def _call(maker, *args):
    def make():
        return maker() + tuple(args), {}
    return make


CALLS = [
    _call(_runner(), [Literal(1.5), Literal(2.5)]),                   # full
    _call(_runner(), [Literal(2.5), Literal(1.5)]),                   # full, other order
    _call(_runner(), [Literal(1.5), Literal(3.5)]),                   # wrong_expected
    _call(_runner(), [Literal(1.5)]),                                 # fewer than found
    _call(_runner(values=(1.5, 1.5)), [Literal(1.5)]),                # duplicate
    _call(_runner(type_=False), []),                                  # no_type, passes
    _call(_runner(type_=False), [Literal(1.5), Literal(2.5)]),        # no_type, fails
    _call(_runner(link=False), []),                                   # no_link, passes
    _call(_runner(link=False), [Literal(1.5), Literal(2.5)]),         # no_link, fails
    _call(_runner(link_sample=SAMPLE2), []),                          # other_sample, passes
    _call(_runner(link_sample=SAMPLE2), [Literal(1.5), Literal(2.5)]),  # other_sample, fails
    _call(_runner(expected_data={"melt_viscosity_data": [Literal(1.5)]}), None),  # none_expected
    _call(_runner(), None),                                           # none_no_data
]

VERDICT = run_pair(
    __file__,
    entry='test_melt_viscosity',
    calls=CALLS,
)
