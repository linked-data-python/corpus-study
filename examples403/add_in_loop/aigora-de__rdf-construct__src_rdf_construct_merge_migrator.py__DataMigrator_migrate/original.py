# Extracted from aigora-de/rdf-construct@670e400ea4 : src/rdf_construct/merge/migrator.py
# region: DataMigrator.migrate (lines 94-156, stratum add_in_loop)
# licence of the source repository: see meta.json
from rdflib import Graph, URIRef, Literal, BNode
from rdf_construct.merge.config import MigrationRule, DataMigrationConfig

def migrate(
    self,
    data: Graph,
    uri_map: dict[URIRef, URIRef] | None = None,
    rules: list[MigrationRule] | None = None,
) -> MigrationResult:
    """Migrate a data graph.

    Args:
        data: Source data graph to migrate
        uri_map: Simple URI substitution map (old -> new)
        rules: Complex migration rules to apply

    Returns:
        MigrationResult with migrated graph and statistics
    """
    result = MigrationResult()
    result.source_triples = len(data)

    # Create a new graph for the migrated data
    migrated = Graph()

    # Copy namespace bindings
    for prefix, ns in data.namespace_manager.namespaces():
        migrated.bind(prefix, ns)

    # Phase 1: Apply simple URI substitutions
    if uri_map:
        for s, p, o in data:
            new_s = self._substitute_uri(s, uri_map, result.stats, is_subject=True)
            new_o = self._substitute_uri(o, uri_map, result.stats, is_subject=False)
            migrated.add((new_s, p, new_o))
    else:
        # No substitutions, just copy
        for triple in data:
            migrated.add(triple)

    # Phase 2: Apply complex transformation rules
    if rules:
        for rule in rules:
            if rule.type == "rename":
                # Handle rename rules that weren't in uri_map
                if rule.from_uri and rule.to_uri:
                    single_map = {URIRef(rule.from_uri): URIRef(rule.to_uri)}
                    migrated = self._apply_uri_substitution(migrated, single_map, result.stats)
                    result.stats.rules_applied[rule.description or "rename"] = (
                        result.stats.rules_applied.get(rule.description or "rename", 0) + 1
                    )

            elif rule.type == "transform":
                changes = self.rule_engine.apply_rule(migrated, rule)
                result.stats.triples_added += changes.get("added", 0)
                result.stats.triples_removed += changes.get("removed", 0)
                result.stats.rules_applied[rule.description or "transform"] = (
                    result.stats.rules_applied.get(rule.description or "transform", 0)
                    + changes.get("instances", 0)
                )

    result.migrated_graph = migrated
    result.result_triples = len(migrated)
    result.success = True

    return result
