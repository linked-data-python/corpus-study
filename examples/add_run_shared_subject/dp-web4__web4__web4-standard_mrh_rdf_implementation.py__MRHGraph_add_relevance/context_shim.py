# Context shim (see meta.json): stands in for the dp-web4/web4 MRHGraph
# instance that add_relevance reads/writes through self, plus the two
# upstream types it needs merely to be *defined* -- MRHEdge is used as a
# parameter type annotation, evaluated at def-time since the source has no
# `from __future__ import annotations`, and MRHRelation is the enum
# edge.relation is drawn from in the fixtures below.
# (web4-standard/mrh_rdf_implementation.py, dp-web4/web4@16038c9d58.)
#
# MRHRelation and MRHEdge are copied verbatim (enum member for member,
# dataclass field for field) from that commit. MRHGraphStub duck-types only
# the two attributes add_relevance actually touches (self.graph, self.edges)
# -- not the rest of the real MRHGraph (entity_id, grounding_edges,
# _setup_namespaces), which this region never reads. Identical shim imported
# by both original.py and translated.ldpy.
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional

from rdflib import Graph


class MRHRelation(Enum):
    """Standard MRH relationship types (verbatim, see meta.json)."""
    DERIVES_FROM = "derives_from"
    SPECIALIZES = "specializes"
    CONTRADICTS = "contradicts"
    EXTENDS = "extends"
    REFERENCES = "references"
    DEPENDS_ON = "depends_on"
    ALTERNATIVES_TO = "alternatives_to"
    PRODUCES = "produces"
    CONSUMES = "consumes"
    TRANSFORMS = "transforms"
    BINDING = "binding"
    PAIRING = "pairing"
    WITNESSING = "witnessing"
    BROADCAST = "broadcast"
    GROUNDING = "grounding"


@dataclass
class MRHEdge:
    """Represents an edge in the MRH graph (verbatim, see meta.json)."""
    target_lct: str
    probability: float
    relation: MRHRelation
    distance: int = 1
    decay_rate: float = 0.9
    conditional_on: Optional[List[str]] = None
    metadata: Dict = field(default_factory=dict)


class MRHGraphStub:
    """Duck-types the members of MRHGraph that add_relevance uses."""

    def __init__(self):
        self.graph = Graph()
        self.edges = []
