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

Added by the mutation audit of 2026-10-31 (fixture.ttl says why each node
is there; ex:Neighbour, stored first, is what kills the islands widened to
`m{ [] pred ?o }`):
  * two_all        -- two owl:allValuesFrom values: `.first()` like
                       `g.value`, where `.one()` raises -> True.
  * empty_all      -- owl:allValuesFrom "" (falsy literal) -> fallback -> True.
  * no_base        -- zero solutions for someValuesFrom -> False.
  * no_datatype    -- zero solutions for onDatatype -> False.
  * iri_some       -- someValuesFrom is an IRI (itself carrying an
                       owl:onDatatype), guard skips -> False.
  * both_all       -- truthy allValuesFrom skips the fallback -> True.
  * (no_restriction now also meets a NAMED class with owl:onProperty
    fhir:value, which the isinstance(node, BNode) test must skip.)
  * non_xsd_some   -- fallback reaching a non-xsd datatype -> False.
  * repo_<name>    -- one call per FHIR primitive of the repository's own
                       fhir.ttl (fhir_primitives.ttl), the inputs of
                       test_primitives (test_fhir_ttl.py:39), integer64 included.
The printed lines ("type failure ...", "No base type ...") are compared too.
"""
import os

from rdflib import Namespace, RDFS

from rdfeval.harness import fixture_graph, run_pair

FIXTURE = "fixture.ttl"
REPO_DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fhir_primitives.ttl")
EX = Namespace("http://example.org/")
FHIR_NS = Namespace("http://hl7.org/fhir/")


def _fixture_call(name):
    def call():
        g = fixture_graph(FIXTURE)
        return ((EX[name], g), {})
    call.__name__ = name
    return call


def _repo_call(prim):
    def call():
        g = fixture_graph(REPO_DATA)
        return ((prim, g), {})
    call.__name__ = "repo_" + prim.split("/")[-1]
    return call


NEW_CALLS = [_fixture_call(n) for n in
             ("TwoAll", "EmptyAll", "NoBase", "NoDatatype", "IriSome", "NonXsdSome", "BothAll")]
REPO_CALLS = [_repo_call(p) for p in sorted(
    fixture_graph(REPO_DATA).subjects(RDFS.subClassOf, FHIR_NS.Primitive))]


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
    calls=[string_primitive, code_primitive, bad_primitive, integer64_primitive, no_restriction]
          + NEW_CALLS + REPO_CALLS,
    # ordered=True only if the region imposes an order (sorted, ORDER BY):
    # no store promises one, so results are compared as multisets. Each
    # call's fixture node has at most one rdfs:subClassOf restriction whose
    # owl:onProperty is fhir:value, so the outer loop's iteration order
    # never affects the result.
)
