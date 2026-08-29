"""Validation driver for isamplesorg__vocabularies__tools_navocab___init__.py__VocabularyStore_narrower.

This region READS a graph, so the oracle is not isomorphism but the equality
of the values both versions produce from the same input graph (design record
corpus/405). `fixture.ttl` is parsed fresh for each side (design record's
"several solutions / zero solution / non-matching neighbourhood" recipe).

`narrower` is an unbound method (`self, concept, v=None, abbreviate=False`):
`self` needs `._g`, `.expand_name`, `._one_res` (which itself calls
`.compact_name`) -- the three members the region actually reads. `_Store`
below is a stand-in with the upstream bodies of exactly those three methods
(tools/navocab/__init__.py:214-238), not a copy of the whole VocabularyStore
class. It defines `__eq__`/`__hash__` by graph isomorphism because `narrower`
never mutates `self._g`, so a passing run always has both sides' stand-ins
isomorphic -- the harness would otherwise fall back to identity comparison
on two separately-constructed instances and report a false diff on `arg[0]`.
"""
from pathlib import Path

from rdflib.compare import isomorphic

from rdfeval.harness import run_pair, fixture_graph

FIXTURE = Path(__file__).resolve().parent / "fixture.ttl"


class _Store:
    def __init__(self):
        self._g = fixture_graph(FIXTURE)

    def expand_name(self, n):
        if n is None:
            return n
        try:
            return self._g.namespace_manager.expand_curie(n)
        except (ValueError, TypeError):
            pass
        return n

    def compact_name(self, n):
        if n is None:
            return n
        try:
            import rdflib
            return rdflib.URIRef(n).n3(self._g.namespace_manager)
        except (ValueError, TypeError):
            pass
        return n

    def _one_res(self, rows, abbreviate=False):
        res = []
        for r in rows:
            if abbreviate:
                res.append(self.compact_name(r[0]))
            else:
                res.append(r[0])
        return res

    def __eq__(self, other):
        return isinstance(other, _Store) and isomorphic(self._g, other._g)

    def __hash__(self):
        return 0


def call(concept, v=None, abbreviate=False):
    return lambda: ((_Store(), concept, v), {"abbreviate": abbreviate})


VERDICT = run_pair(
    __file__,
    entry='narrower',
    calls=[
        call("ex:Animal"),                       # several solutions: Dog, Cat, Wolf
        call("ex:Animal", "ex:VocabA"),           # scheme filter excludes Wolf
        call("ex:Rock"),                          # zero solutions
        call("ex:Animal", abbreviate=True),       # abbreviate path (compact_name)
    ],
)
