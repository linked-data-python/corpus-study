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

The repository calls the region once per triples map of ONE graph
(rml_validate.py:1170, ``for tm in _triples_map_subjects(graph)``), so a
single map in the graph cannot tell ``{tm}`` from a variable.  The later
calls therefore exercise the scope of every anchor and the predicate tuples:

  call[1]  the inline graph plus a second map ``tm2`` (its own reference
           "foreign" and its own one-column function "foreign_fn"); called on
           ``tm``: neither must appear (kills ``{tm}`` -> ``?_t``, the cut
           ``?pom`` link, and ``{om}`` -> ``?_o`` in the functionExecution
           island).
  call[2]  the same graph, called on ``tm2``: what ``tm`` transcribes must
           not appear in turn.
  call[3]  ``fixture_mapping.ttl``, a mapping in the shape the repository
           really parses (IRI triples maps, BLANK-NODE predicate-object and
           object maps, the legacy ``rml#reference`` and ``fnml#`` namespaces,
           the w3id ``rml:termType rml:IRI``, a predicate-object map with two
           object maps, neighbours reached through ``rr:predicateMap``, the
           subject map, or a predicate other than ``rr:predicateObjectMap``);
           called on ``ex:SampleMap``.  Every member of
           ``_TERM_TYPE_PREDS``, ``_REFERENCE_PREDS`` and
           ``_FUNCTION_EXECUTION_PREDS`` decides the answer, so truncating
           any tuple changes it.
  call[4]  the same fixture on ``ex:CurveMap`` (the neighbour map).
  call[5]  the same fixture on ``ex:EmptyMap``: no predicate-object map, the
           zero-solution case, an empty set.
  call[6]  an IRI that is no subject of the graph at all: an empty set too.

Every call gets a freshly built or freshly parsed graph per side, and the
triples maps are URIRefs, as ``_triples_map_subjects`` yields them for the
repository's mappings (``<#Map> a rr:TriplesMap``).
"""
from rdflib import Graph, Literal, URIRef

from pathlib import Path

from rdfeval.harness import fixture_graph, run_pair

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


TM2 = URIRef("http://example.org/tm2")


def _build_two_maps() -> Graph:
    """The inline graph plus a second triples map that ``tm`` must not read."""
    g, _tm = _build_graph()
    pom = URIRef("http://example.org/tm2_pom")
    om_ref = URIRef("http://example.org/tm2_om_ref")
    om_fn = URIRef("http://example.org/tm2_om_fn")
    g.add((TM2, URIRef(R2RML + "predicateObjectMap"), pom))
    g.add((pom, URIRef(R2RML + "objectMap"), om_ref))
    g.add((om_ref, URIRef(RML + "reference"), Literal("foreign")))
    g.add((pom, URIRef(R2RML + "objectMap"), om_fn))
    fe = URIRef("http://example.org/tm2_fe")
    g.add((om_fn, URIRef(RML + "functionExecution"), fe))
    inp = URIRef("http://example.org/tm2_inp")
    g.add((fe, URIRef(RML + "input"), inp))
    ivm = URIRef("http://example.org/tm2_ivm")
    g.add((inp, URIRef(RML + "inputValueMap"), ivm))
    g.add((ivm, URIRef(RML + "reference"), Literal("foreign_fn")))
    return g


def _case_two_maps_tm():
    return (_build_two_maps(), URIRef("http://example.org/tm")), {}


def _case_two_maps_tm2():
    return (_build_two_maps(), TM2), {}


FIXTURE = Path(__file__).resolve().parent / "fixture_mapping.ttl"
MAPPING = "http://example.org/mapping#"


def _fixture_case(local):
    return lambda: ((fixture_graph(FIXTURE), URIRef(MAPPING + local)), {})


VERDICT = run_pair(
    __file__,
    entry='_tm_transcribed_columns',
    calls=[
        _case,
        _case_two_maps_tm,
        _case_two_maps_tm2,
        _fixture_case("SampleMap"),
        _fixture_case("CurveMap"),
        _fixture_case("EmptyMap"),
        _fixture_case("NotAMap"),
    ],
)
