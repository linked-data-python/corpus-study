"""Validation driver for isamplesorg__vocabularies__tools_navocab___init__.py__VocabularyStore_broader.

This region READS a graph, so the oracle is not isomorphism but the equality
of the values both versions produce from the same input graph (design record
corpus/405). `fixture.ttl` is parsed fresh for each side (design record's
"several solutions / zero solution / non-matching neighbourhood" recipe).

`broader` is an unbound method (`self, concept, v=None, abbreviate=False`):
`self` needs `._g`, `.expand_name`, `._one_res` (which itself calls
`.compact_name`) -- the three members the region actually reads. `_Store`
below is a stand-in with the upstream bodies of exactly those three methods
(tools/navocab/__init__.py:214-238), not a copy of the whole VocabularyStore
class. It defines `__eq__`/`__hash__` by graph isomorphism because `broader`
never mutates `self._g`, so a passing run always has both sides' stand-ins
isomorphic -- the harness would otherwise fall back to identity comparison
on two separately-constructed instances and report a false diff on `arg[0]`.

The real input type (audit of 2026-10-31, same finding as the sibling
region VocabularyStore_narrower).  The repository calls `broader` with a
full IRI as a `str`: tools/tests/test_navocab.py:70-77 (`test_broader`
expects 1 then 0 results for the `str` ".../level1b" then ".../rootterm"),
and tools/vocab.py:230-247, whose CLI passes the command-line `concept` and
`vocabulary` strings.  For such a `str`, `expand_name` returns it unchanged,
so the original binds a `str` through `initBindings`.  The store is
rdflib-sqlalchemy (`ConjunctiveGraph("SQLAlchemy")`,
tools/navocab/__init__.py:97), which matches a bound term by its TEXT: a
subject always (base.py `build_subject_clause`), an object in the IRI and
literal partitions alike unless it is a `Literal`, which only matches
literals (STRONGLY_TYPED_TERMS = False, store.py:132, 467-484).
`_SQLTextStore` reproduces that rule on rdflib's Memory store (the package
is not installed in the study's venv).  The calls on it exercise:

- a full IRI `str`, v=None: several solutions (Animal, Mammal, Canid);
- a full IRI `str` concept and `str` scheme: the scheme filter (Mammal out),
  and Canid in through its LITERAL skos:inScheme carrying VocabA's text --
  a `Literal` binding of the scheme would keep Canid and lose Animal;
- a full IRI `str` with abbreviate=True (the CLI default), and a CURIE
  concept with a `str` scheme (the two expand_name outcomes in one query);
- a CURIE on that store (URIRef bindings);
- Rock as a full IRI `str`: zero solutions (test_broader's root case);
- an empty `str` scheme (the CLI's `vocabulary` argument is a `str`): the
  `v is None` guard must still take the scheme branch, which matches nothing.

The first four calls, on the in-memory graph, are kept as they were.
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
    text, in the IRI and literal partitions alike; a bound Literal object
    matches literals only, by text, plus its datatype / language when it has
    one.  (The rdf:type partition, which the region's queries never reach,
    is not distinguished.)  Same class as in the sibling narrower driver."""

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
    entry='broader',
    calls=[
        call("ex:Dog"),                          # several solutions: Animal, Mammal
        call("ex:Dog", "ex:VocabA"),              # scheme filter excludes Mammal
        call("ex:Rock"),                          # zero solutions
        call("ex:Dog", abbreviate=True),          # abbreviate path (compact_name)
        # the store and the input type of the repository (see the docstring)
        call_sql("http://example.org/Dog"),
        call_sql("http://example.org/Dog", "http://example.org/VocabA"),
        call_sql("http://example.org/Dog", abbreviate=True),
        call_sql("ex:Dog", "http://example.org/VocabA"),
        call_sql("ex:Dog"),
        call_sql("http://example.org/Rock"),
        call_sql("http://example.org/Dog", ""),  # falsy str scheme: v-branch, no match
    ],
)
