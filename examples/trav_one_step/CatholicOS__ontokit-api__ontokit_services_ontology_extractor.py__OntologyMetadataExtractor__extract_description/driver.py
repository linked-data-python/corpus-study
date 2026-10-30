"""Validation driver for CatholicOS__ontokit-api__ontokit_services_ontology_extractor.py__OntologyMetadataExtractor__extract_description.

This region READS a graph, so the oracle is not isomorphism but the equality
of the values both versions produce from the same input graph (design record
corpus/405).  `fixture.ttl` is parsed fresh for each side.

_extract_description(self, graph, ontology_iri) needs more than the graph
(and it is a bound method whose body never touches `self`), so `calls=`
supplies (self, graph, ontology_iri) explicitly.

Five calls against the shared fixture, plus one against a fresh empty graph:

1. ontology_iri=ex:OntoDC -- dc:description must win over dcterms:description
   and rdfs:comment (priority order).
2. ontology_iri=ex:OntoDCTERMS -- no dc:description, so dcterms:description
   wins over rdfs:comment.
3. ontology_iri=ex:OntoComment -- only rdfs:comment is present.
4. ontology_iri=ex:OntoEmpty -- ex:OntoEmpty itself has none of the three
   properties, so the per-subject loop finds nothing for it. The region's
   code, despite its own comment ("If no ontology IRI, search globally"),
   does NOT gate the second loop on `ontology_iri` being falsy: it always
   runs after the first loop comes up empty. This call proves the
   translation preserves that quirk rather than "fixing" it: it must fall
   through to the global rdf:type owl:Ontology search and return whichever
   of ex:OntoDC/ex:OntoDCTERMS/ex:OntoComment/ex:OntoEmpty the store yields
   first for that pattern -- same value original.py's graph.subjects(...)
   and translated.ldpy's m{ ?s rdf:type owl:Ontology } must agree on,
   whatever it is (the harness compares the two return values against each
   other, not against a hand-predicted string).
5. ontology_iri=None -- subjects_to_check is empty from the start, so only
   the global search loop ever runs; same fixture, exercises the
   m{ ?s rdf:type owl:Ontology } read directly.
6. A fresh, unrelated, empty Graph() with ontology_iri=None -- the true
   zero-solution case: both loops find nothing, and both versions must
   return None. (A truly empty result cannot be reached against the shared
   fixture: as long as any owl:Ontology subject with a description exists
   anywhere in it, the unconditional second loop -- see call 4 above -- will
   always find one. This call uses its own graph instead, still fresh per
   side as required.)

ex:NotAnOntology in fixture.ttl carries a dc:description but is never typed
owl:Ontology and is never passed as ontology_iri: the neighbourhood that
must not leak into any of the six results above.

Calls 1-6 never take the global loop past its first subject: ex:OntoDC comes
first in the store and has a dc:description, so the global read
`?s rdf:type owl:Ontology` and the reads inside that loop were not pinned
down.  Calls 7-12, added at repair (2026-10-30), each run on their own
small fixture (fresh per side) and decide one of them:

7. fixture_no_described_ontology.ttl, ontology_iri=None -- the only
   owl:Ontology has no description, the descriptions sit on an owl:Class
   and on a subject linked to owl:Ontology by rdfs:seeAlso: the answer is
   None.  Widening rdf:type or owl:Ontology into a variable, or the subject
   of the reads in the global loop, returns a description instead.
8. same fixture, ontology_iri=ex:OntoBare -- the first loop finds nothing
   for a subject given explicitly, and the global loop too: None.
9. fixture_second_ontology.ttl, ontology_iri=None -- the first owl:Ontology
   in store order has no description, the second (a blank node) has only
   rdfs:comment: the global loop must reach its second subject and the last
   property of the priority list, and interpolate a BNode.
10. fixture_empty_values.ttl, ontology_iri=ex:OntoEmptyValue -- two
    dc:description values, "" first: `if value:` must skip "" and keep
    reading the same property (the second value wins over dcterms).
11. same fixture, ontology_iri=None -- the same through the global loop.
12. fixture.ttl, ontology_iri="" -- a falsy str, the type the repository
    passes (ontology_extractor.py:150, from _find_ontology_iri, a str or
    None): no subject to check, global loop only.
"""
from pathlib import Path

from rdflib import Graph, Namespace

from rdfeval.harness import fixture_graph, run_pair

HERE = Path(__file__).resolve().parent
FIXTURE = HERE / "fixture.ttl"

EX = Namespace("http://example.org/")

SELF = object()  # the region's body never reads `self`


def call_dc_priority():
    return ((SELF, fixture_graph(FIXTURE), str(EX.OntoDC)), {})


def call_dcterms_fallback():
    return ((SELF, fixture_graph(FIXTURE), str(EX.OntoDCTERMS)), {})


def call_comment_fallback():
    return ((SELF, fixture_graph(FIXTURE), str(EX.OntoComment)), {})


def call_global_fallthrough_quirk():
    return ((SELF, fixture_graph(FIXTURE), str(EX.OntoEmpty)), {})


def call_no_ontology_iri_global_search():
    return ((SELF, fixture_graph(FIXTURE), None), {})


def call_zero_solutions():
    return ((SELF, Graph(), None), {})


def _on(name, iri):
    def case():
        return ((SELF, fixture_graph(HERE / name),
                 None if iri is None else str(iri)), {})
    case.__name__ = f"call_{name}_{iri}"
    return case


REPAIR_CALLS = [
    _on("fixture_no_described_ontology.ttl", None),
    _on("fixture_no_described_ontology.ttl", EX.OntoBare),
    _on("fixture_second_ontology.ttl", None),
    _on("fixture_empty_values.ttl", EX.OntoEmptyValue),
    _on("fixture_empty_values.ttl", None),
    _on("fixture.ttl", ""),
]


VERDICT = run_pair(
    __file__,
    entry='_extract_description',
    fixture="fixture.ttl",
    calls=[call_dc_priority, call_dcterms_fallback, call_comment_fallback,
           call_global_fallthrough_quirk, call_no_ontology_iri_global_search,
           call_zero_solutions] + REPAIR_CALLS,
    # ordered=True only if the region imposes an order (sorted, ORDER BY):
    # no store promises one, so results are compared as multisets.
)
