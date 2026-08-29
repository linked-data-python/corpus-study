# Context shim (see meta.json): subset of src/rdf_construct/shacl/converters.py
# from aigora-de/rdf-construct@670e400ea43804775652dc94751a85e33e04ba23, so the
# region executes outside the package. Identical bindings for both
# representations.
#
# PropertyConstraint is the dataclass the region builds and returns
# (unmodified, minus the `merge` method the region never calls).
#
# CardinalityConverter stands in for the real class only as the `self`
# receiver `convert_for_class` needs: its `_is_datatype` override (the class
# defines its OWN, simpler than the base Converter's -- no XSD_DATATYPES set)
# is reproduced verbatim; it has no other state, so a single shared instance
# can be reused as `self` on both sides of every call (see driver.py).

from dataclasses import dataclass, field

from rdflib import Graph, RDF, RDFS, URIRef, XSD


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
    in_values: list = field(default_factory=list)
    pattern: str | None = None
    min_inclusive: object = None
    max_inclusive: object = None
    order: int | None = None


class CardinalityConverter:
    """Stand-in receiver: only the method the region calls on `self`."""

    def _is_datatype(self, uri: URIRef, graph: Graph) -> bool:
        """Check if URI represents a datatype."""
        return str(uri).startswith(str(XSD)) or (uri, RDF.type, RDFS.Datatype) in graph
