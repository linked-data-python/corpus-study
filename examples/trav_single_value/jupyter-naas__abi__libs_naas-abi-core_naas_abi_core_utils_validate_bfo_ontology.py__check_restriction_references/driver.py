"""Validation driver for jupyter-naas__abi__libs_naas-abi-core_naas_abi_core_utils_validate_bfo_ontology.py__check_restriction_references.

This region READS a graph (several `g.value`/`g.subjects` calls over
owl:Restriction bnodes), so the oracle is not isomorphism of a graph the
region builds but the equality of what the two versions produce from the same
input (design record corpus/405): each call parses a fresh graph for each
side and passes it as the sole argument `g`.  The repository itself passes a
`Graph` parsed from a Turtle file (validate_bfo_ontology.py, `g.parse(...,
format="turtle")`), which is what every call below passes too.  The result is
a list of issue dicts, compared as a multiset.

Call 0 is `fixture.ttl` (see its own header): several restrictions reached
from different owners, both filler predicates, the vocabulary-prefix and
declared-term branches of `_is_known`, WARNING against ERROR severity, an
orphan restriction (no owner, `continue`).  Its restrictions are named IRIs
and every `_is_known` decision there is taken before the graph-membership
test, so the calls after it add one small graph per read of the region, with
blank-node restrictions as real ontologies write them:

1. `bool(m{ {iri} a ?x })`, the `(iri, RDF.type, None) in g` branch: IRIs
   known ONLY through an rdf:type triple (one as onProperty, one as a
   someValuesFrom filler), next to an IRI that has triples but no rdf:type
   (`?p` in place of `a` would call it known) and an IRI that is only the
   OBJECT of an rdf:type triple (a reversed pattern would call it known).
   The undeclared someValuesFrom filler also kills a filler loop that
   forgets owl:someValuesFrom.
2. `m{ ?s a owl:DatatypeProperty }`: a declared datatype property as
   onProperty, not flagged.  A mutant that empties this set survives: every
   declared datatype property carries an rdf:type triple, so the
   graph-membership test of `_is_known` covers it (same redundancy in the
   original).
3. cardinality of the three `.first()` reads: one restriction with TWO
   undeclared onProperty values, TWO undeclared allValuesFrom fillers and
   TWO owners.  `g.value` takes the first and does not raise; `.one()` would.
4. values that are absent or not IRIs: a restriction with no onProperty and
   no filler; a literal onProperty and a blank-node filler (both skipped by
   `isinstance(..., URIRef)`); an orphan restriction with an undeclared
   someValuesFrom filler (the `continue` of the filler loop), which only has
   an OUTGOING rdfs:subClassOf edge (a reversed owner pattern would find an
   owner); two restrictions reached only through owl:equivalentClass, one
   with an undeclared onProperty and one with an undeclared someValuesFrom
   filler (`?p` in place of rdfs:subClassOf, in either owner lookup, would
   find an owner).
5. the restriction scan `m{ ?bnode a owl:Restriction }`: a node typed
   owl:Class, and a node that has owl:Restriction as the object of another
   predicate, each with an owner and an undeclared onProperty: neither is a
   restriction, neither may be flagged.
6. falsy terms: the empty IRI `<>` (URIRef(""), falsy) as an owner (the
   `if owner else "unknown"` branches) and as an undeclared onProperty;
   built programmatically, since Turtle resolves `<>` against a base.
7. the empty graph: no restriction, no issue.
"""
from rdflib import BNode, Graph, OWL, RDF, RDFS, URIRef

from rdfeval.harness import fixture_graph, run_pair

FIXTURE = "fixture.ttl"

PREFIXES = """\
@prefix ex:   <http://example.org/> .
@prefix ext:  <http://external.example/> .
@prefix owl:  <http://www.w3.org/2002/07/owl#> .
@prefix rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
"""

TYPED_ONLY = """
ext:typedProp a ext:PropertyKind .
ext:TypedThing a ext:Kind .
ext:labelOnly rdfs:label "has triples, no rdf:type" .
ext:someIndividual a ext:objectOfType .
ex:C1 rdfs:subClassOf [ a owl:Restriction ;
    owl:onProperty ext:typedProp ; owl:someValuesFrom ext:TypedThing ] .
ex:C2 rdfs:subClassOf [ a owl:Restriction ;
    owl:onProperty ext:typedProp ; owl:allValuesFrom ext:labelOnly ] .
ex:C3 rdfs:subClassOf [ a owl:Restriction ;
    owl:onProperty ext:typedProp ; owl:someValuesFrom ext:objectOfType ] .
"""

DATATYPE_PROPERTY = """
ext:dataProp a owl:DatatypeProperty .
ex:D1 rdfs:subClassOf [ a owl:Restriction ; owl:onProperty ext:dataProp ] .
"""

TWO_VALUES = """
_:r a owl:Restriction ;
    owl:onProperty ext:p1, ext:p2 ;
    owl:allValuesFrom ext:F1, ext:F2 .
ex:OwnerA rdfs:subClassOf _:r .
ex:OwnerB rdfs:subClassOf _:r .
"""

ABSENT_OR_NOT_IRI = """
ex:E1 rdfs:subClassOf [ a owl:Restriction ] .
ex:E2 rdfs:subClassOf [ a owl:Restriction ;
    owl:onProperty "ext:notAnIri" ;
    owl:allValuesFrom [ a owl:Class ] ] .
_:orphan a owl:Restriction ;
    owl:someValuesFrom ext:orphanFiller ;
    rdfs:subClassOf ex:Parent .
ex:Eq owl:equivalentClass [ a owl:Restriction ;
    owl:onProperty ext:eqProp ] .
ex:Eq2 owl:equivalentClass [ a owl:Restriction ;
    owl:someValuesFrom ext:eqFiller ] .
"""

NOT_A_RESTRICTION = """
ex:N1 rdfs:subClassOf [ a owl:Class ; owl:onProperty ext:classProp ] .
ex:N2 rdfs:subClassOf [ rdfs:seeAlso owl:Restriction ;
    owl:onProperty ext:seeAlsoProp ] .
"""

TURTLE_CASES = [TYPED_ONLY, DATATYPE_PROPERTY, TWO_VALUES,
                ABSENT_OR_NOT_IRI, NOT_A_RESTRICTION]


def from_fixture():
    return ((fixture_graph(FIXTURE),), {})


def from_turtle(body):
    def case():
        return ((Graph().parse(data=PREFIXES + body, format="turtle"),), {})
    return case


def falsy_terms():
    g = Graph()
    empty = URIRef("")
    r = BNode()
    g.add((r, RDF.type, OWL.Restriction))
    g.add((r, OWL.onProperty, empty))
    g.add((empty, RDFS.subClassOf, r))
    return ((g,), {})


def empty_graph():
    return ((Graph(),), {})


VERDICT = run_pair(
    __file__,
    entry='check_restriction_references',
    fixture=FIXTURE,
    calls=([from_fixture] + [from_turtle(body) for body in TURTLE_CASES]
           + [falsy_terms, empty_graph]),
    # ordered=True only if the region imposes an order (sorted, ORDER BY):
    # no store promises one, so results are compared as multisets.
)
