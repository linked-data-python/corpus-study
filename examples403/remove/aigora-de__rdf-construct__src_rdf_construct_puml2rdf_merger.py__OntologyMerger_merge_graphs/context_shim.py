# Context shim (see meta.json): the MergeResult dataclass and the class
# attributes of OntologyMerger that surround the region in
# src/rdf_construct/puml2rdf/merger.py, copied verbatim from
# aigora-de/rdf-construct@670e400ea4 so that the region executes outside its
# package.  Identical bindings for both representations.
#
# The two methods of OntologyMerger are left out: `merge_graphs` IS the region,
# and `merge` only parses a file before delegating to it.
from dataclasses import dataclass

from rdflib import Graph, RDF, RDFS


@dataclass
class MergeResult:
    """Result of merging two graphs."""

    graph: Graph
    added_count: int = 0
    updated_count: int = 0
    preserved_count: int = 0
    conflicts: list[str] = None

    def __post_init__(self):
        if self.conflicts is None:
            self.conflicts = []


class OntologyMerger:
    """Merges generated RDF with existing ontology content."""

    # Predicates that PlantUML defines authoritatively
    AUTHORITATIVE_PREDICATES = {
        RDF.type,
        RDFS.subClassOf,
        RDFS.domain,
        RDFS.range,
        RDFS.subPropertyOf,
    }

    # Predicates to merge (keep both if different)
    MERGEABLE_PREDICATES = {
        RDFS.label,
        RDFS.comment,
        RDFS.seeAlso,
    }

    def __init__(self, preserve_existing: bool = True) -> None:
        self.preserve_existing = preserve_existing
