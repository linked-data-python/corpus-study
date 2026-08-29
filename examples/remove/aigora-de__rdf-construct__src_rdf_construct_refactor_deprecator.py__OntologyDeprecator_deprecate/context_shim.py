# Context shim (see meta.json): the three dataclasses that
# src/rdf_construct/refactor/deprecator.py defines around the region, copied
# verbatim from aigora-de/rdf-construct@670e400ea4 so that the region executes
# outside its package.  Identical bindings for both representations.
#
# `OntologyDeprecator` itself is not needed: the region never touches `self`.
from dataclasses import dataclass, field

from rdflib import Graph


@dataclass
class EntityDeprecationInfo:
    """Information about a deprecated entity."""

    uri: str
    found: bool = True
    current_labels: list[str] = field(default_factory=list)
    current_comments: list[str] = field(default_factory=list)
    was_already_deprecated: bool = False
    triples_added: int = 0
    reference_count: int = 0
    replaced_by: str | None = None
    message: str | None = None


@dataclass
class DeprecationStats:
    """Statistics from a deprecation operation."""

    entities_deprecated: int = 0
    entities_not_found: int = 0
    entities_already_deprecated: int = 0
    triples_added: int = 0


@dataclass
class DeprecationResult:
    """Result of a deprecation operation."""

    deprecated_graph: Graph | None = None
    stats: DeprecationStats = field(default_factory=DeprecationStats)
    success: bool = True
    error: str | None = None
    entity_info: list[EntityDeprecationInfo] = field(default_factory=list)
    source_triples: int = 0
    result_triples: int = 0
