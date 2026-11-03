# Extracted from CatholicOS/ontokit-api@23680a4d04 : ontokit/services/ontology_extractor.py
# region: OntologyMetadataExtractor._extract_description (lines 386-415, stratum trav_one_step)
# licence of the source repository: see meta.json
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import DC, DCTERMS, OWL, RDF, RDFS

def _extract_description(self, graph: Graph, ontology_iri: str | None) -> str | None:
    """
    Extract the description from the ontology.

    Priority: dc:description > dcterms:description > rdfs:comment
    """
    # Define subjects to check (ontology IRI first)
    subjects_to_check: list[URIRef | None] = [URIRef(ontology_iri)] if ontology_iri else []
    # If no ontology IRI, search globally for any description on owl:Ontology subjects
    subjects_to_check += graph.subjects(RDF.type, OWL.Ontology)

    # Priority order for description properties
    desc_properties = [DC.description, DCTERMS.description, RDFS.comment]

    for subject in subjects_to_check:
        for prop in desc_properties:
            for obj in graph.objects(subject, prop):
                value = str(obj)
                if value:
                    return value

    return None
