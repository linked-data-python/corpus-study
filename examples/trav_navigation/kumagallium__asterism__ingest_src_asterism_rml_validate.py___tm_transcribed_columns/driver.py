"""Validation driver for kumagallium__asterism__ingest_src_asterism_rml_validate.py___tm_transcribed_columns.

Establishes semantic equivalence of original.py and translated.ldpy.  The
region is a pure function of ``(graph, tm)``, so the fixture is built inline
here (no fixture.ttl: the oracle is isomorphism/value-equality of the
returned set, not a reading-region comparison against a shared Turtle file,
per meta.json).

The fixture graph covers: a direct ``rml:reference`` object map (included),
a ``rr:termType rr:IRI`` object map (excluded outright), a function pipeline
reading exactly one column through a nested transform (included), a function
pipeline combining two columns (excluded), and a predicateObjectMap whose
objectMap has neither a reference nor a functionExecution (contributes
nothing) — so the join over predicateObjectMap/objectMap must not silently
drop or duplicate any of these independent siblings under the same
triples-map.
"""
from rdflib import Graph, Literal, URIRef

from rdfeval.harness import run_pair

RML = "http://w3id.org/rml/"
R2RML = "http://www.w3.org/ns/r2rml#"


def _build_graph() -> Graph:
    g = Graph()
    tm = URIRef("http://example.org/tm")

    def pom_om(pom_id, om_id):
        pom = URIRef(f"http://example.org/{pom_id}")
        om = URIRef(f"http://example.org/{om_id}")
        g.add((tm, URIRef(R2RML + "predicateObjectMap"), pom))
        g.add((pom, URIRef(R2RML + "objectMap"), om))
        return om

    # 1. direct rml:reference to column "name" -> included
    om1 = pom_om("pom1", "om1")
    g.add((om1, URIRef(RML + "reference"), Literal("name")))

    # 2. rr:termType rr:IRI -> excluded outright, even though it also has a
    #    reference (the is_iri guard must short-circuit before it is read).
    om2 = pom_om("pom2", "om2")
    g.add((om2, URIRef(R2RML + "termType"), URIRef(R2RML + "IRI")))
    g.add((om2, URIRef(RML + "reference"), Literal("id")))

    # 3. function pipeline reading exactly one column ("age"), through a
    #    nested transform (number_clean(round(age))) -> included, once.
    om3 = pom_om("pom3", "om3")
    fe_outer = URIRef("http://example.org/fe_outer")
    g.add((om3, URIRef(RML + "functionExecution"), fe_outer))
    inp_outer = URIRef("http://example.org/inp_outer")
    g.add((fe_outer, URIRef(RML + "input"), inp_outer))
    ivm_outer = URIRef("http://example.org/ivm_outer")
    g.add((inp_outer, URIRef(RML + "inputValueMap"), ivm_outer))
    fe_inner = URIRef("http://example.org/fe_inner")
    g.add((ivm_outer, URIRef(RML + "functionExecution"), fe_inner))
    inp_inner = URIRef("http://example.org/inp_inner")
    g.add((fe_inner, URIRef(RML + "input"), inp_inner))
    ivm_inner = URIRef("http://example.org/ivm_inner")
    g.add((inp_inner, URIRef(RML + "inputValueMap"), ivm_inner))
    g.add((ivm_inner, URIRef(RML + "reference"), Literal("age")))

    # 4. function pipeline combining two distinct columns -> excluded.
    om4 = pom_om("pom4", "om4")
    fe_two = URIRef("http://example.org/fe_two")
    g.add((om4, URIRef(RML + "functionExecution"), fe_two))
    for col, suffix in (("first_name", "a"), ("last_name", "b")):
        inp = URIRef(f"http://example.org/inp_{suffix}")
        g.add((fe_two, URIRef(RML + "input"), inp))
        ivm = URIRef(f"http://example.org/ivm_{suffix}")
        g.add((inp, URIRef(RML + "inputValueMap"), ivm))
        g.add((ivm, URIRef(RML + "reference"), Literal(col)))

    # 5. neither reference nor functionExecution -> contributes nothing.
    pom_om("pom5", "om5")

    return g, tm


def _case():
    g, tm = _build_graph()
    return (g, tm), {}


VERDICT = run_pair(
    __file__,
    entry='_tm_transcribed_columns',
    calls=[_case],
)
