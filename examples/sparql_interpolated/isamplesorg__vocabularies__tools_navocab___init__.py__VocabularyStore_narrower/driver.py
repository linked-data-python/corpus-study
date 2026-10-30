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

The real input type (repair of 2026-10-30).  The repository calls `narrower`
with a full IRI as a `str`: tools/vocab.py:278-282 (`concept =
str(_s.getVocabRoot(vocabulary)[0])`, then `s.narrower(c, v, ...)`), and
tools/tests/test_navocab.py:62-66, which expects 3 then 2 results for the
`str` "https://w3id.org/.../rootterm".  For such a `str`, `expand_name`
returns it unchanged (`expand_curie` raises ValueError), so the original
binds a `str` through `initBindings`.  And the store is not an in-memory
graph: `VocabularyStore._initialize_store` opens
`rdflib.ConjunctiveGraph("SQLAlchemy", ...)` (tools/navocab/__init__.py:97).
rdflib-sqlalchemy (0.5.4) matches a bound term by its TEXT
(`table.c.object == obj`, base.py `build_object_clause`) and, with
`STRONGLY_TYPED_TERMS = False` (store.py:132), searches the literal
partition for every object and the IRI partition for every object that is
not a `Literal` (store.py:467-484), adding a datatype / language clause only
for a `Literal` that carries one (base.py:114-125).  So the original's `str`
matches the IRI with that text -- the repository's own test relies on it --
and a `Literal` would only match literals.

That package is not installed in the study's environment (nor is
SQLAlchemy), so `_SQLTextStore` below reproduces exactly that matching rule
on top of rdflib's Memory store, and `_SQLStore` is `_Store` on it.  The
calls on it exercise:

- a full IRI as `str`, v=None: several solutions (Dog, Cat, Wolf) plus Ghost,
  whose skos:broader is a LITERAL with the Animal IRI's text -- the store
  returns it for a `str` binding, so both sides must;
- full IRI `str` concept and `str` scheme: the scheme filter (Wolf out), Ghost
  in through its literal skos:inScheme;
- a full IRI `str` with abbreviate=True: compact_name on the results;
- a CURIE concept with a full IRI `str` scheme: the two expand_name outcomes
  (URIRef, unchanged `str`) in one query;
- a CURIE on that store: an URIRef binding must behave as on the memory
  store, plus the text match on Ghost;
- Rock as a full IRI `str`: zero solutions.

The first four calls, on the in-memory graph, are kept as they were.  No
call passes a `str` IRI to the in-memory graph: there the original's `str`
matches nothing at all, a store the repository never uses.
"""
from pathlib import Path

from rdflib import Graph, Literal
from rdflib.compare import isomorphic
from rdflib.plugins.stores.memory import Memory

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


class _SQLTextStore(Memory):
    """rdflib-sqlalchemy's matching rule (STRONGLY_TYPED_TERMS = False) on a
    Memory store: a bound subject, predicate or non-Literal object matches by
    text, in the IRI and literal partitions alike; a bound Literal matches
    literals only, by text, plus its datatype / language when it has one.
    (The rdf:type partition, which the region's queries never reach, is not
    distinguished.)"""

    def triples(self, pattern, context=None):
        s, p, o = pattern
        for (ts, tp, to), ctxs in super().triples((None, None, None), context):
            if s is not None and str(ts) != str(s):
                continue
            if p is not None and str(tp) != str(p):
                continue
            if o is not None:
                if isinstance(o, Literal):
                    if not isinstance(to, Literal) or str(to) != str(o):
                        continue
                    if o.datatype is not None and to.datatype != o.datatype:
                        continue
                    if o.language is not None and to.language != o.language:
                        continue
                elif str(to) != str(o):
                    continue
            yield (ts, tp, to), ctxs


class _SQLStore(_Store):
    def __init__(self):
        self._g = Graph(store=_SQLTextStore()).parse(FIXTURE, format="turtle")

    def __eq__(self, other):
        return isinstance(other, _SQLStore) and isomorphic(self._g, other._g)

    def __hash__(self):
        return 0


def call(concept, v=None, abbreviate=False):
    return lambda: ((_Store(), concept, v), {"abbreviate": abbreviate})


def call_sql(concept, v=None, abbreviate=False):
    return lambda: ((_SQLStore(), concept, v), {"abbreviate": abbreviate})


VERDICT = run_pair(
    __file__,
    entry='narrower',
    calls=[
        call("ex:Animal"),                       # several solutions: Dog, Cat, Wolf
        call("ex:Animal", "ex:VocabA"),           # scheme filter excludes Wolf
        call("ex:Rock"),                          # zero solutions
        call("ex:Animal", abbreviate=True),       # abbreviate path (compact_name)
        # the store and the input type of the repository (see the docstring)
        call_sql("http://example.org/Animal"),
        call_sql("http://example.org/Animal", "http://example.org/VocabA"),
        call_sql("http://example.org/Animal", abbreviate=True),
        call_sql("ex:Animal", "http://example.org/VocabA"),
        call_sql("ex:Animal"),
        call_sql("http://example.org/Rock"),
    ],
)
