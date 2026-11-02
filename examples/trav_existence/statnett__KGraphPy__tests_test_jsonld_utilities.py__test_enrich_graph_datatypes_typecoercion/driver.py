"""Validation driver for statnett__KGraphPy__tests_test_jsonld_utilities.py__test_enrich_graph_datatypes_typecoercion.

The region is a self-contained test: it builds its own graph, calls
`enrich_graph_datatypes` and asserts two things about the result. It takes no
argument and returns None, so a green call proves nothing by itself. What the
original SHOWS is whether it raises -- and the only thing that can make it
raise is the function under test. The driver therefore installs, before each
call, a variant of `kgraphpy_shim.enrich_graph_datatypes` in the function
object the region imported (its `__code__`; same for both representations),
the real one first, then variants that break the outcome in different ways:

  real          the real function: both literals are re-typed -> passes.
  noop          does nothing: the float stays a float -> the first assertion
                fails.
  untyped_only  re-types only the literals WITHOUT a datatype (case 1 of the
                real function): the float keeps its datatype -> the first
                assertion fails, the second would hold.
  typed_only    re-types only the literals with a WRONG datatype (case 2): the
                plain literal stays plain -> the second assertion fails, the
                first would hold.
  wrong_type    re-types both, to xsd:decimal instead of the mapped
                xsd:integer: both assertions fail (the neighbouring literals
                exist, with another datatype).
  keeps_old     adds the re-typed literals WITHOUT removing the old ones: the
                graph holds both, and both assertions (existence only) hold.
  lexical       re-types through the lexical form (`Literal(str(o.value), ...)`
                rather than `Literal(o.value, ...)`): the float becomes
                "30.0"^^xsd:integer as before, the plain literal likewise ->
                passes.
  int_form      re-types through int(): the float becomes "30"^^xsd:integer,
                not the "30.0" the assertion looks for -> the first assertion
                fails (the lexical form is part of the term).

The asserts carry no message: a failing call raises a bare AssertionError, and
which of the two fired is not told apart, only whether the call passes.
"""
from rdflib import Literal, URIRef

from rdfeval.harness import run_pair
import kgraphpy_shim

REAL = kgraphpy_shim.enrich_graph_datatypes.__code__


def _noop(graph, dt_map):
    return None


def _untyped_only(graph, dt_map):
    add, remove = [], []
    for s, p, o in graph:
        if str(p) in dt_map and isinstance(o, Literal) and o.datatype is None:
            remove.append((s, p, o))
            add.append((s, p, Literal(o.value, datatype=URIRef(dt_map[str(p)]))))
    for t in remove:
        graph.remove(t)
    for t in add:
        graph.add(t)


def _typed_only(graph, dt_map):
    add, remove = [], []
    for s, p, o in graph:
        if (str(p) in dt_map and isinstance(o, Literal) and o.datatype is not None
                and o.datatype != URIRef(dt_map[str(p)])):
            remove.append((s, p, o))
            add.append((s, p, Literal(o.value, datatype=URIRef(dt_map[str(p)]))))
    for t in remove:
        graph.remove(t)
    for t in add:
        graph.add(t)


def _wrong_type(graph, dt_map):
    add, remove = [], []
    for s, p, o in graph:
        if str(p) in dt_map and isinstance(o, Literal):
            remove.append((s, p, o))
            add.append((s, p, Literal(o.value, datatype=URIRef("http://www.w3.org/2001/XMLSchema#decimal"))))
    for t in remove:
        graph.remove(t)
    for t in add:
        graph.add(t)


def _keeps_old(graph, dt_map):
    add = []
    for s, p, o in graph:
        if str(p) in dt_map and isinstance(o, Literal):
            add.append((s, p, Literal(o.value, datatype=URIRef(dt_map[str(p)]))))
    for t in add:
        graph.add(t)


def _lexical(graph, dt_map):
    add, remove = [], []
    for s, p, o in graph:
        if str(p) in dt_map and isinstance(o, Literal):
            remove.append((s, p, o))
            add.append((s, p, Literal(str(o.value), datatype=URIRef(dt_map[str(p)]))))
    for t in remove:
        graph.remove(t)
    for t in add:
        graph.add(t)


def _int_form(graph, dt_map):
    add, remove = [], []
    for s, p, o in graph:
        if str(p) in dt_map and isinstance(o, Literal):
            remove.append((s, p, o))
            value = int(o.value) if isinstance(o.value, float) else o.value
            add.append((s, p, Literal(value, datatype=URIRef(dt_map[str(p)]))))
    for t in remove:
        graph.remove(t)
    for t in add:
        graph.add(t)


def _case(code):
    def make():
        kgraphpy_shim.enrich_graph_datatypes.__code__ = code
        return (), {}
    return make


CALLS = [
    _case(REAL),                       # real
    _case(_noop.__code__),             # noop
    _case(_untyped_only.__code__),     # untyped_only
    _case(_typed_only.__code__),       # typed_only
    _case(_wrong_type.__code__),       # wrong_type
    _case(_keeps_old.__code__),        # keeps_old
    _case(_lexical.__code__),          # lexical
    _case(_int_form.__code__),         # int_form
]

VERDICT = run_pair(
    __file__,
    entry='test_enrich_graph_datatypes_typecoercion',
    calls=CALLS,
)
