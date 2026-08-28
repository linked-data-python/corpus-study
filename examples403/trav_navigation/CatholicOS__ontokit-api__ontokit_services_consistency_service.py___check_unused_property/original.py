# Extracted from CatholicOS/ontokit-api@23680a4d04 : ontokit/services/consistency_service.py
# region: _check_unused_property (lines 117-136, stratum trav_navigation)
# licence of the source repository: see meta.json
from rdflib import Graph, URIRef
from rdflib.namespace import DCTERMS, OWL, RDF, RDFS, SKOS, XSD
from ontokit.schemas.quality import ConsistencyCheckResult, ConsistencyIssue
_PROPERTY_TYPES = {OWL.ObjectProperty, OWL.DatatypeProperty, OWL.AnnotationProperty, RDF.Property}

def _check_unused_property(graph: Graph) -> list[ConsistencyIssue]:
    """Property not used as predicate in any triple (excluding own declaration)."""
    issues = []
    for prop_type in _PROPERTY_TYPES:
        for prop in graph.subjects(RDF.type, prop_type):
            if not isinstance(prop, URIRef):
                continue
            # Check if this property is used as a predicate anywhere
            used = any(s != prop for s in graph.subjects(prop, None))
            if not used:
                issues.append(
                    ConsistencyIssue(
                        rule_id="unused_property",
                        severity="warning",
                        entity_iri=str(prop),
                        entity_type="property",
                        message="Property is declared but never used as a predicate",
                    )
                )
    return issues
