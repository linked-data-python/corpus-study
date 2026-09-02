# Context shim (see meta.json), for aigora-de/rdf-construct@670e400ea4,
# src/rdf_construct/shacl/converters.py and .../shacl/namespaces.py.
#
# SH: original.py's `from .namespaces import SH` is a relative import that
# raises `ImportError: attempted relative import with no known parent
# package` outside the rdf_construct package. Copied verbatim from
# src/rdf_construct/shacl/namespaces.py (the module also defines a
# DefinedNamespace subclass SHACL with typed term access, but the extracted
# region only ever reaches SH.<term> / SH["class"] / SH["in"], never SHACL,
# so only SH is reproduced).
#
# _create_rdf_list: a module-level helper the region calls
# (`_create_rdf_list(shapes_graph, self.in_values)`) that sits just past the
# extracted lines (88-141 of converters.py; the helper is at 144-168),
# copied verbatim.
#
# PropertyConstraint: the dataclass `to_rdf` is a method of. Reproduced with
# its field shape only (types and defaults, docstrings trimmed) -- the
# region reads every field but calls no method on it (`.merge`, defined on
# the real class, is not reached and is not reproduced).
#
# Identical bindings for both representations.
from dataclasses import dataclass, field

from rdflib import BNode, Graph, Literal, Namespace, RDF, URIRef

SH = Namespace("http://www.w3.org/ns/shacl#")


def _create_rdf_list(graph: Graph, items: list) -> BNode:
    """Create an RDF list from a Python list."""
    if not items:
        return RDF.nil

    head = BNode()
    current = head

    for i, item in enumerate(items):
        graph.add((current, RDF.first, item))

        if i < len(items) - 1:
            next_node = BNode()
            graph.add((current, RDF.rest, next_node))
            current = next_node
        else:
            graph.add((current, RDF.rest, RDF.nil))

    return head


@dataclass
class PropertyConstraint:
    """Represents a property constraint to be added to a shape."""

    path: URIRef
    node_class: URIRef | None = None
    datatype: URIRef | None = None
    min_count: int | None = None
    max_count: int | None = None
    node_kind: URIRef | None = None
    name: str | None = None
    description: str | None = None
    in_values: list[URIRef | Literal] = field(default_factory=list)
    pattern: str | None = None
    min_inclusive: Literal | None = None
    max_inclusive: Literal | None = None
    order: int | None = None
