# Extracted from JonasHeinickeBio/biomedical-knowledge-lookup@00477184b3 : src/knowledge_lookup/services/rdf_converter.py
# region: UnifiedRDFConverter._add_concept_mappings (lines 687-717, stratum add_in_loop)
# licence of the source repository: see meta.json
from rdflib import RDF, RDFS, Graph, Literal, Namespace, URIRef
from context_shim import ConceptType, KnowledgeSource, UnifiedConcept

def _add_concept_mappings(self, graph: Graph, concept: UnifiedConcept, concept_uri: URIRef):
    """Add RDF triples for concept mappings."""
    mappings = concept.mappings or []
    for mapping in mappings:
        # Create URIs for source and target concepts
        to_uri = self._get_concept_uri_from_identifier(mapping.to_concept)  # type: ignore[arg-type]

        # Add mapping relationship
        mapping_predicate = self.namespaces.VOCAB.hasMapping
        graph.add((concept_uri, mapping_predicate, to_uri))

        # Add mapping metadata
        mapping_uri = self.namespaces.AIDPAIS[
            f"mapping/{concept.primary_id}_{mapping.from_concept.identifier}_{mapping.to_concept.identifier}"
        ]
        graph.add((mapping_uri, self.namespaces.RDF.type, self.namespaces.VOCAB.Mapping))
        graph.add(
            (mapping_uri, self.namespaces.VOCAB.mappingType, Literal(mapping.mapping_type))
        )
        if mapping.confidence:
            graph.add(
                (
                    mapping_uri,
                    self.namespaces.VOCAB.confidenceScore,
                    Literal(mapping.confidence, datatype=self.namespaces.XSD.float),
                )
            )
        if mapping.source:
            graph.add(
                (mapping_uri, self.namespaces.VOCAB.mappingSource, Literal(mapping.source))
            )


# Demo harness (identical on both sides, see meta.json): _add_concept_mappings
# takes `self` as an explicit parameter (a bound-method extraction), and the
# driver's per-call argument comparison would otherwise compare that stand-in
# object by identity (always unequal, since each side builds its own
# instance) -- so this wraps the call and returns only what the region
# actually produces: the graph it wrote into.
def demo(concept, concept_uri):
    from rdflib import Graph
    from context_shim import ConverterStub
    graph = Graph()
    _add_concept_mappings(ConverterStub(), graph, concept, concept_uri)
    return graph
