"""Validation driver for
BD2KOnFHIR__fhirtordf__tests_fhir_tests_test_fhir_ttl.py__FHIRTTLTestCase_is_xsd_primitive.

This region READS a graph, so the oracle is not isomorphism but the equality
of the values both versions produce from the same input graph (design record
corpus/405).  `fixture.ttl` is parsed fresh for each side.

`is_xsd_primitive(prim, g)` takes `prim` as an external argument (a fixed,
named IRI here, no BNode lookup indirection needed), so a bare `fixture=`
is not enough. Each call below exercises one branch of the function against
its own freshly-parsed fixture graph:

  * string_primitive    -- ordinary xsd:string base type via allValuesFrom
                            (the modern fhir.ttl shape) -> True.
  * code_primitive       -- someValuesFrom/onDatatype fallback path,
                            resolving to xsd:token -> True.
  * bad_primitive        -- base type is a non-xsd IRI -> False (the "type
                            failure" branch).
  * integer64_primitive  -- base type is exactly fhir:integer64, the
                            FHIRCat #35 special case -> True despite not
                            being xsd:-prefixed.
  * no_restriction       -- no restriction on fhir:value matches at all
                            (a named subClassOf, one on a different
                            property, one blank node with no
                            owl:onProperty triple): the trav_single_value
                            zero-solution case -> False.
None of the calls ever passes ex:Other, the fixture's neighbourhood.
"""
from rdflib import Namespace

from rdfeval.harness import fixture_graph, run_pair

FIXTURE = "fixture.ttl"
EX = Namespace("http://example.org/")


def string_primitive():
    g = fixture_graph(FIXTURE)
    return ((EX.StringPrimitive, g), {})


def code_primitive():
    g = fixture_graph(FIXTURE)
    return ((EX.CodePrimitive, g), {})


def bad_primitive():
    g = fixture_graph(FIXTURE)
    return ((EX.BadPrimitive, g), {})


def integer64_primitive():
    g = fixture_graph(FIXTURE)
    return ((EX.Integer64Primitive, g), {})


def no_restriction():
    g = fixture_graph(FIXTURE)
    return ((EX.NoRestriction, g), {})


VERDICT = run_pair(
    __file__,
    entry='is_xsd_primitive',
    fixture=FIXTURE,
    calls=[string_primitive, code_primitive, bad_primitive, integer64_primitive, no_restriction],
    # ordered=True only if the region imposes an order (sorted, ORDER BY):
    # no store promises one, so results are compared as multisets. Each
    # call's fixture node has at most one rdfs:subClassOf restriction whose
    # owl:onProperty is fhir:value, so the outer loop's iteration order
    # never affects the result.
)
