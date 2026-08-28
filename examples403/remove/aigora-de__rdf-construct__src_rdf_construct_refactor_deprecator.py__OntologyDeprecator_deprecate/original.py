# Extracted from aigora-de/rdf-construct@670e400ea4 : src/rdf_construct/refactor/deprecator.py
# region: OntologyDeprecator.deprecate (lines 112-219, stratum remove)
# licence of the source repository: see meta.json
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, RDFS, OWL, DCTERMS
DCTERMS = Namespace("http://purl.org/dc/terms/")

def deprecate(
    self,
    graph: Graph,
    entity: str,
    replaced_by: str | None = None,
    message: str | None = None,
    version: str | None = None,
) -> DeprecationResult:
    """Mark a single entity as deprecated.

    Args:
        graph: Source RDF graph (will be modified in-place).
        entity: URI of entity to deprecate.
        replaced_by: Optional URI of replacement entity.
        message: Optional deprecation message.
        version: Optional version when deprecated.

    Returns:
        DeprecationResult with updated graph.
    """
    result = DeprecationResult()
    result.source_triples = len(graph)

    entity_uri = URIRef(entity)
    info = EntityDeprecationInfo(uri=entity)

    # Check if entity exists in the graph
    entity_exists = False
    for s, p, o in graph:
        if s == entity_uri:
            entity_exists = True
            break
        if o == entity_uri:
            info.reference_count += 1

    if not entity_exists:
        # Entity not found as subject - check if it's referenced
        info.found = False
        result.stats.entities_not_found += 1
        result.entity_info.append(info)
        result.deprecated_graph = graph
        result.result_triples = len(graph)
        return result

    # Get current labels and comments
    for label in graph.objects(entity_uri, RDFS.label):
        if isinstance(label, Literal):
            info.current_labels.append(str(label))

    for comment in graph.objects(entity_uri, RDFS.comment):
        if isinstance(comment, Literal):
            info.current_comments.append(str(comment))

    # Check if already deprecated
    for obj in graph.objects(entity_uri, OWL.deprecated):
        if str(obj).lower() == "true":
            info.was_already_deprecated = True
            result.stats.entities_already_deprecated += 1
            break

    # Add owl:deprecated true (if not already present)
    if not info.was_already_deprecated:
        graph.add((entity_uri, OWL.deprecated, Literal(True)))
        info.triples_added += 1
        result.stats.entities_deprecated += 1

    # Add dcterms:isReplacedBy if replacement specified
    if replaced_by:
        replaced_by_uri = URIRef(replaced_by)
        # Remove any existing isReplacedBy
        graph.remove((entity_uri, DCTERMS.isReplacedBy, None))
        graph.add((entity_uri, DCTERMS.isReplacedBy, replaced_by_uri))
        info.triples_added += 1
        info.replaced_by = replaced_by

    # Add/update deprecation comment
    if message:
        # Build full deprecation message
        deprecation_msg = f"DEPRECATED: {message}"
        if version:
            deprecation_msg = f"DEPRECATED (v{version}): {message}"
        info.message = deprecation_msg

        # Check if there's an existing comment to update
        existing_deprecated_comment = None
        for comment in list(graph.objects(entity_uri, RDFS.comment)):
            if isinstance(comment, Literal) and str(comment).startswith("DEPRECATED"):
                existing_deprecated_comment = comment
                break

        if existing_deprecated_comment:
            # Remove old deprecation comment
            graph.remove((entity_uri, RDFS.comment, existing_deprecated_comment))

        # Add new deprecation comment
        graph.add((entity_uri, RDFS.comment, Literal(deprecation_msg, lang="en")))
        info.triples_added += 1

    # Ensure dcterms namespace is bound
    graph.bind("dcterms", DCTERMS, override=False)

    result.stats.triples_added += info.triples_added
    result.entity_info.append(info)
    result.deprecated_graph = graph
    result.result_triples = len(graph)
    result.success = True

    return result
