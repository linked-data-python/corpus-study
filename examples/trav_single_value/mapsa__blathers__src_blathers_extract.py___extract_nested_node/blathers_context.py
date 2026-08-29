# Context shim (see meta.json): reduced from src/blathers/extract.py at
# mapsa/blathers@cad7822217 (NestedRow, ExtractedNestedNode, _str_or_none,
# _local_name, _term_label) -- module-level names the region's own lines
# reference but do not define, outside the tirage's captured context window
# (OntologyData and the other Extracted* dataclasses, the rest of the
# extraction pipeline, are not reproduced: unused by this region). Verbatim
# from the source file. Identical bindings for both representations.
from __future__ import annotations

from dataclasses import dataclass, field

from rdflib import RDFS


def _local_name(iri: str) -> str:
    """Extract the local name from an IRI (after # or last /)."""
    if "#" in iri:
        return iri.split("#")[-1]
    return iri.rsplit("/", 1)[-1]


def _str_or_none(val) -> str | None:
    return str(val) if val is not None else None


@dataclass
class NestedRow:
    """One predicate on a nested blank node, labelled from the graph."""
    property_iri: str
    label: str
    values: list[str] = field(default_factory=list)


@dataclass
class ExtractedNestedNode:
    """A single blank node attached to a class via a domain property."""
    comment: str | None = None
    rows: list[NestedRow] = field(default_factory=list)


def _term_label(g, iri) -> str:
    """rdfs:label of a term, falling back to its local name."""
    return _str_or_none(g.value(iri, RDFS.label)) or _local_name(str(iri))
