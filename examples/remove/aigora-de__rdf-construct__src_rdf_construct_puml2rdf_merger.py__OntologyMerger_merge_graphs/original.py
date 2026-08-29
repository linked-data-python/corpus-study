# Extracted from aigora-de/rdf-construct@670e400ea4 : src/rdf_construct/puml2rdf/merger.py
# region: OntologyMerger.merge_graphs (lines 102-172, stratum remove)
# licence of the source repository: see meta.json
from rdflib import Graph, Namespace, URIRef, RDF, RDFS
from context_shim import MergeResult, OntologyMerger

def merge_graphs(
    self,
    new_graph: Graph,
    existing: Graph,
) -> MergeResult:
    """Merge two graphs.

    Args:
        new_graph: Newly generated RDF graph
        existing: Existing ontology graph

    Returns:
        MergeResult with merged graph and statistics
    """
    result = MergeResult(graph=Graph())
    conflicts = []

    # Copy all prefixes from both
    for prefix, ns in existing.namespace_manager.namespaces():
        result.graph.bind(prefix, ns, override=False)
    for prefix, ns in new_graph.namespace_manager.namespaces():
        result.graph.bind(prefix, ns, override=False)

    # Get all subjects defined in new graph
    new_subjects = set(new_graph.subjects())

    # Process existing triples
    for s, p, o in existing:
        if s in new_subjects:
            # Subject is also in new graph - check for conflicts
            if p in self.AUTHORITATIVE_PREDICATES:
                # New graph is authoritative for these
                new_values = set(new_graph.objects(s, p))
                if new_values:
                    # Will be added from new graph
                    result.updated_count += 1
                    continue
                else:
                    # Keep existing if not in new
                    result.graph.add((s, p, o))
                    result.preserved_count += 1
            elif p in self.MERGEABLE_PREDICATES:
                # Keep existing and add new if different
                result.graph.add((s, p, o))
                result.preserved_count += 1
            else:
                # Other predicates - preserve existing
                result.graph.add((s, p, o))
                result.preserved_count += 1
        else:
            # Subject only in existing - preserve
            result.graph.add((s, p, o))
            result.preserved_count += 1

    # Add triples from new graph
    for s, p, o in new_graph:
        if (s, p, o) not in result.graph:
            # Check for conflicting values on authoritative predicates
            if p in self.AUTHORITATIVE_PREDICATES:
                existing_values = list(result.graph.objects(s, p))
                for ev in existing_values:
                    if ev != o:
                        conflicts.append(f"Conflict on {s} {p}: existing={ev}, new={o}")
                        if not self.preserve_existing:
                            result.graph.remove((s, p, ev))

            result.graph.add((s, p, o))
            result.added_count += 1

    result.conflicts = conflicts
    return result


# Demo harness (identical on both sides, see meta.json): the region returns a
# MergeResult, a dataclass whose Graph field rdflib compares by store
# identifier -- never equal across two runs.  This entry point hands back the
# merged graph itself (compared by isomorphism) and the four statistics the
# region computed.
def demo(new_graph, existing, preserve_existing=True):
    result = merge_graphs(OntologyMerger(preserve_existing), new_graph, existing)
    return (result.graph, result.added_count, result.updated_count,
            result.preserved_count, sorted(result.conflicts))
