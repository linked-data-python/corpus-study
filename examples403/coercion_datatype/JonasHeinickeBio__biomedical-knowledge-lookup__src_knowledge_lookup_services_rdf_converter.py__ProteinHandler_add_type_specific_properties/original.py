# Extracted from JonasHeinickeBio/biomedical-knowledge-lookup@00477184b3 : src/knowledge_lookup/services/rdf_converter.py
# region: ProteinHandler.add_type_specific_properties (lines 327-349, stratum coercion_datatype)
# licence of the source repository: see meta.json
from rdflib import RDF, RDFS, Graph, Literal, Namespace, URIRef
from ..models import ConceptType, KnowledgeSource, UnifiedConcept

def add_type_specific_properties(
    self, graph: Graph, concept: UnifiedConcept, concept_uri: URIRef
):
    """Add protein-specific properties."""
    for identifier in concept.identifiers or []:
        if identifier.source == KnowledgeSource.UNIPROT:
            uniprot_uri = self.namespaces.UNIPROT[identifier.identifier]
            graph.add((concept_uri, self.namespaces.VOCAB.hasUniProtId, uniprot_uri))
            graph.add((uniprot_uri, self.namespaces.OWL.sameAs, concept_uri))

        elif identifier.source == KnowledgeSource.ENSEMBL:
            ensembl_uri = self.namespaces.ENSEMBL[identifier.identifier]
            graph.add((concept_uri, self.namespaces.VOCAB.hasEnsemblId, ensembl_uri))
            graph.add((ensembl_uri, self.namespaces.OWL.sameAs, concept_uri))

        # Add generic cross-reference
        graph.add(
            (
                concept_uri,
                self.namespaces.VOCAB.hasIdentifier,
                Literal(f"{str(identifier.source)}:{identifier.identifier}"),
            )
        )
