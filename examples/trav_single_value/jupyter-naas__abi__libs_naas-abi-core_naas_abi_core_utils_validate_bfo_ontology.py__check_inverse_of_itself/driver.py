"""Validation driver for jupyter-naas__abi__libs_naas-abi-core_naas_abi_core_utils_validate_bfo_ontology.py__check_inverse_of_itself.

This region READS a graph (`g.value(prop, OWL.inverseOf)` per prop in
main_properties), so the oracle is not isomorphism of a graph the region
builds but the equality of what the two versions produce from the same input
(design record corpus/405): every call builds its graph afresh for each side
and passes it as `g`; `main_properties` is the driver's second argument.  In
the repository (validate_bfo_ontology.py, `main_properties = {s for s in
g_main.subjects(RDF.type, OWL.ObjectProperty) if isinstance(s, URIRef)}`,
and `combined = Graph()` filled by `.add`), the graph is a plain in-memory
`Graph` and every property a `URIRef`: that is what every call passes.

Call 0 is `fixture.ttl` (see its header): several solutions of the pattern,
the zero-solution case, and a self-inverse property left out of
main_properties.  The calls after it each decide one more thing:

1. which value `g.value` takes when there are SEVERAL.  `g.value` (any=True)
   does not raise: it answers the first object `g.triples((prop, p, None))`
   yields, i.e. the store's insertion order, and `m{ }.first()` walks the
   same `triples()`.  The graph is built with `.add`, in a stated order, as
   the repository's `combined` graph is:
   * ex:firstSelf -- owl:inverseOf ex:firstSelf, THEN ex:other: the first
     value is the property itself, flagged.  `ex:intruder owl:inverseOf
     ex:firstSelf` is added before them, so a reversed pattern
     (`?x owl:inverseOf {prop}`) reads ex:intruder and does not flag it;
   * ex:laterSelf -- owl:inverseOf ex:other, THEN ex:laterSelf: the first
     value is NOT the property, not flagged, although the property is among
     its values (kills "any value equals prop", "the last value", and the
     reversed pattern, whose only subject here is ex:laterSelf itself).
   `.one()` raises on both.
2. neighbours sharing two of the three terms of `{prop} owl:inverseOf ?v`:
   ex:subSelf rdfs:subPropertyOf ex:subSelf and ex:eqSelf
   owl:equivalentProperty ex:eqSelf (a widened predicate would flag them);
   ex:litSelf owl:inverseOf the LITERAL spelling of its own IRI (Literal !=
   URIRef, not flagged; a string comparison would flag it); ex:bnodeInv
   owl:inverseOf a blank node.
3. `_short`/`_label` read the graph's prefixes, and `@graph g` binds the
   block's `owl:` on the caller's graph (record ldpy/027): a self-inverse
   property IN the owl namespace, from a file that spells that namespace
   `o:`, with no rdfs:label -- the reported `subject` and message are the
   qname the graph's own bindings give.
4. a property absent from the graph altogether (no triple at all), and an
   empty main_properties (no issue, whatever the graph).
5. the empty graph, with properties to check: no solution anywhere.
"""
from rdflib import BNode, Graph, Literal, OWL, RDFS, URIRef

from rdfeval.harness import fixture_graph, run_pair

FIXTURE = "fixture.ttl"
EX = "http://example.org/"


def ex(local):
    return URIRef(EX + local)


MAIN_PROPERTIES = {
    URIRef("http://example.org/selfInverse"),
    URIRef("http://example.org/hasPart"),
    URIRef("http://example.org/partOf"),
    URIRef("http://example.org/noInverse"),
    # ex:otherSelfInverse deliberately excluded: it is self-inverse in the
    # fixture too, but must never be reached by this call.
}


def one_call():
    return ((fixture_graph(FIXTURE), set(MAIN_PROPERTIES)), {})


def several_values():
    g = Graph()
    g.bind("ex", EX)
    # insertion order is what g.value and m{ }.first() both follow
    g.add((ex("intruder"), OWL.inverseOf, ex("firstSelf")))
    g.add((ex("firstSelf"), OWL.inverseOf, ex("firstSelf")))
    g.add((ex("firstSelf"), OWL.inverseOf, ex("other")))
    g.add((ex("firstSelf"), RDFS.label, Literal("First Self")))
    g.add((ex("laterSelf"), OWL.inverseOf, ex("other")))
    g.add((ex("laterSelf"), OWL.inverseOf, ex("laterSelf")))
    return ((g, {ex("firstSelf"), ex("laterSelf")}), {})


def neighbours():
    g = Graph()
    g.bind("ex", EX)
    g.add((ex("subSelf"), RDFS.subPropertyOf, ex("subSelf")))
    g.add((ex("eqSelf"), OWL.equivalentProperty, ex("eqSelf")))
    g.add((ex("litSelf"), OWL.inverseOf, Literal(EX + "litSelf")))
    g.add((ex("bnodeInv"), OWL.inverseOf, BNode()))
    return ((g, {ex("subSelf"), ex("eqSelf"), ex("litSelf"),
                 ex("bnodeInv")}), {})


def owl_namespace_property():
    g = Graph().parse(data="""
        @prefix o: <http://www.w3.org/2002/07/owl#> .
        o:topObjectProperty a o:ObjectProperty ;
            o:inverseOf o:topObjectProperty .
    """, format="turtle")
    return ((g, {OWL.topObjectProperty}), {})


def absent_property():
    g = Graph().parse(data="""
        @prefix ex: <http://example.org/> .
        @prefix owl: <http://www.w3.org/2002/07/owl#> .
        ex:selfInverse owl:inverseOf ex:selfInverse .
    """, format="turtle")
    return ((g, {ex("notInGraph")}), {})


def no_property():
    return ((fixture_graph(FIXTURE), set()), {})


def empty_graph():
    return ((Graph(), {ex("selfInverse"), ex("notInGraph")}), {})


VERDICT = run_pair(
    __file__,
    entry='check_inverse_of_itself',
    fixture=FIXTURE,
    calls=[one_call, several_values, neighbours, owl_namespace_property,
           absent_property, no_property, empty_graph],
    # ordered=True only if the region imposes an order (sorted, ORDER BY):
    # no store promises one, so results are compared as multisets. The loop
    # also walks a Python `set`, whose own iteration order is not a property
    # of the region either.
)
