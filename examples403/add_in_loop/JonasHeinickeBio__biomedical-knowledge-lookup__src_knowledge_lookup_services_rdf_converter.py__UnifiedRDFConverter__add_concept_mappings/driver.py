"""Validation driver for JonasHeinickeBio__biomedical-knowledge-lookup__src_knowledge_lookup_services_rdf_converter.py__UnifiedRDFConverter__add_concept_mappings.

Establishes semantic equivalence of original.py and translated.ldpy.

_add_concept_mappings is a method (`self` is an explicit first parameter):
both original.py and translated.ldpy carry an identical demo(concept,
concept_uri) harness (see meta.json) that builds a fresh
context_shim.ConverterStub as `self` and a fresh Graph() internally, calls
_add_concept_mappings, and returns the graph -- so the driver compares the
graphs demo() returns, not `self` itself (comparing the stub by identity
would report a spurious difference on every call: each side builds its own
instance, and run_pair has no notion of the two sides' objects being "the
same" beyond structural equality).

CALL_1 -- two mappings, both branches of the two optional triples present
(confidence and source both truthy): exercises the add-in-loop sugar's main
path -- one fixed pattern, values varying per mapping, both `?confidence`
and `?mappingSource` bound. `to_concept.source` is UNIPROT on one mapping
and DRUGBANK on the other, walking two of the five branches of
`_get_concept_uri_from_identifier`.

CALL_2 -- concept.mappings is None (`mappings = concept.mappings or []`
falls back to the empty list): the loop must contribute nothing, not raise.

CALL_3 -- one mapping where confidence=0.0 (falsy but not None -- the
`if mapping.confidence:` guard in the original skips the triple even though
a value exists) and source="" (falsy empty string, same guard skips it
too), and mapping_type=None (the original has no guard around
`Literal(mapping.mapping_type)`, so this exercises `Literal(None)` on both
sides identically). `to_concept.source` is UMLS, the fallback branch of
`_get_concept_uri_from_identifier` (`else: AIDPAIS[f"{source}/{id}"]`).
"""
from rdfeval.harness import run_pair
from rdflib import URIRef
from context_shim import ConceptIdentifier, ConceptMapping, KnowledgeSource, UnifiedConcept

CONCEPT_URI = URIRef("http://www.aid-pais-kg.org/concept/C1")


CONCEPT_1 = UnifiedConcept(
    primary_id="C1",
    mappings=[
        ConceptMapping(
            from_concept=ConceptIdentifier(source=KnowledgeSource.CHEMBL, identifier="f1"),
            to_concept=ConceptIdentifier(source=KnowledgeSource.UNIPROT, identifier="t1"),
            mapping_type="exact",
            confidence=0.9,
            source="manual",
        ),
        ConceptMapping(
            from_concept=ConceptIdentifier(source=KnowledgeSource.CHEMBL, identifier="f2"),
            to_concept=ConceptIdentifier(source=KnowledgeSource.DRUGBANK, identifier="t2"),
            mapping_type="broad",
            confidence=0.4,
            source="automatic",
        ),
    ],
)

CONCEPT_2 = UnifiedConcept(primary_id="C2", mappings=None)

CONCEPT_3 = UnifiedConcept(
    primary_id="C3",
    mappings=[
        ConceptMapping(
            from_concept=ConceptIdentifier(source=KnowledgeSource.UMLS, identifier="f3"),
            to_concept=ConceptIdentifier(source=KnowledgeSource.UMLS, identifier="t3"),
            mapping_type=None,
            confidence=0.0,
            source="",
        ),
    ],
)

VERDICT = run_pair(
    __file__,
    entry='demo',
    calls=[
        ((CONCEPT_1, CONCEPT_URI), {}),
        ((CONCEPT_2, CONCEPT_URI), {}),
        ((CONCEPT_3, CONCEPT_URI), {}),
    ],
)
