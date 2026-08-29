# Extracted from JonasHeinickeBio/biomedical-knowledge-lookup@00477184b3 : src/knowledge_lookup/services/rdf_converter.py
# region: ConceptTypeHandler.add_common_properties (lines 94-154, stratum add_in_loop)
# licence of the source repository: see meta.json
from rdflib import RDF, RDFS, Graph, Literal, Namespace, URIRef
from ..models import ConceptType, KnowledgeSource, UnifiedConcept

def add_common_properties(self, graph: Graph, concept: UnifiedConcept, concept_uri: URIRef):
    """Add common properties shared across all concept types."""
    # Basic properties
    graph.add((concept_uri, self.namespaces.RDF.type, self.get_concept_class_uri(concept)))
    graph.add((concept_uri, self.namespaces.RDFS.label, Literal(concept.primary_label)))

    # Concept type
    graph.add(
        (concept_uri, self.namespaces.VOCAB.conceptType, Literal(str(concept.concept_type)))
    )

    # Confidence score
    if concept.confidence_score is not None and concept.confidence_score > 0:
        graph.add(
            (
                concept_uri,
                self.namespaces.VOCAB.confidenceScore,
                Literal(concept.confidence_score, datatype=self.namespaces.XSD.float),
            )
        )

    # Categories
    if concept.categories:
        for category in concept.categories:
            graph.add((concept_uri, self.namespaces.VOCAB.hasCategory, Literal(category)))

    # Synonyms
    if concept.synonyms:
        for synonym in concept.synonyms:
            graph.add((concept_uri, self.namespaces.VOCAB.hasSynonym, Literal(synonym)))

    # Definitions
    if concept.definitions:
        for definition in concept.definitions:
            graph.add((concept_uri, self.namespaces.VOCAB.hasDefinition, Literal(definition)))

    # Semantic types
    if concept.semantic_types:
        for sem_type in concept.semantic_types:
            graph.add((concept_uri, self.namespaces.VOCAB.hasSemanticType, Literal(sem_type)))

    # Labels in different languages
    labels_dict: dict[str, str] = concept.labels if isinstance(concept.labels, dict) else {}
    for lang, label in labels_dict.items():
        graph.add((concept_uri, self.namespaces.RDFS.label, Literal(label, lang=lang)))

    # Relationships
    if concept.parents:
        for parent in concept.parents:
            parent_uri = URIRef(parent)  # Could be enhanced to resolve to proper URIs
            graph.add((concept_uri, self.namespaces.VOCAB.hasParent, parent_uri))

    if concept.children:
        for child in concept.children:
            child_uri = URIRef(child)
            graph.add((concept_uri, self.namespaces.VOCAB.hasChild, child_uri))

    if concept.related:
        for related in concept.related:
            related_uri = URIRef(related)
            graph.add((concept_uri, self.namespaces.VOCAB.relatedTo, related_uri))
