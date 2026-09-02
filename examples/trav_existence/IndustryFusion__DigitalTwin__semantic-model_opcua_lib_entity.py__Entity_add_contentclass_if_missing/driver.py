"""Validation driver for IndustryFusion__DigitalTwin__semantic-model_opcua_lib_entity.py__Entity_add_contentclass_if_missing.

This region READS two graphs (`g`, the one passed in, and `self.e`, the
Entity's own knowledge graph -- see context_shim.py), so the oracle is the
equality of the values both versions produce from the same input graphs
(design record corpus/405), not isomorphism.

`entry` is the `demo` harness both files carry identically (see meta.json):
it builds a fresh `Entity(e_data)`, runs the region, and returns whether
`add_enum_class` was called -- the one observable effect of
`g.value(contentclass, RDF.type) is not None and
self.e.value(contentclass, RDF.type) is None`.

Four calls give all three truth combinations of the `and` (the fourth
combination -- both False -- would need contentclass typed in neither
graph, which is the same case as "typed in g only" restricted to `self.e`,
already covered by case 2's negative half):

  1. typed in `g`, untyped in `self.e`   -> add_enum_class called (True and True)
  2. typed in `g`, ALSO typed in `self.e` -> not called (True and False)
  3. untyped in `g` at all                -> not called (False and True)
  4. untyped in `g`, but typed in `self.e` (contentclass absent from `g`
     entirely) -> not called (False and False), and proves the read of `g`
     is not silently satisfied by `self.e`'s own type triple
"""
from rdflib import Graph, Namespace, RDF

from rdfeval.harness import run_pair

EX = Namespace("http://example.org/")


def _case(g_data: str, e_data: str, contentclass):
    def make():
        g = Graph().parse(data=g_data, format="turtle") if g_data else Graph()
        e = Graph().parse(data=e_data, format="turtle") if e_data else Graph()
        return (g, e, contentclass), {}
    return make


VERDICT = run_pair(
    __file__,
    entry="demo",
    calls=[
        # 1. g types it, self.e does not -> add_enum_class IS called
        _case(
            "@prefix ex: <http://example.org/> . ex:c1 a ex:Thing .",
            "@prefix ex: <http://example.org/> . ex:other a ex:Thing .",
            EX.c1,
        ),
        # 2. g types it, self.e ALSO types it -> not called
        _case(
            "@prefix ex: <http://example.org/> . ex:c2 a ex:Thing .",
            "@prefix ex: <http://example.org/> . ex:c2 a ex:OtherThing .",
            EX.c2,
        ),
        # 3. g does not type it (untyped neighbour only) -> not called
        _case(
            "@prefix ex: <http://example.org/> . ex:c3 ex:label \"x\" .",
            "",
            EX.c3,
        ),
        # 4. g has nothing at all for it, self.e types it -> not called
        _case(
            "",
            "@prefix ex: <http://example.org/> . ex:c4 a ex:Thing .",
            EX.c4,
        ),
    ],
)
