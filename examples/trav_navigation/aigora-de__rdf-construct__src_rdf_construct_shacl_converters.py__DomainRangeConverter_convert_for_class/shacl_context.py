# Context shim (see meta.json): subset of src/rdf_construct/shacl/converters.py
# and src/rdf_construct/shacl/config.py from aigora-de/rdf-construct@670e400ea4,
# so the region executes outside the package. Identical bindings for both
# representations.
from dataclasses import dataclass, field

from rdflib import Graph, Literal, RDF, RDFS, URIRef, XSD


@dataclass
class PropertyConstraint:
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
    min_inclusive: Literal | None = None
    max_inclusive: Literal | None = None
    order: int | None = None


@dataclass
class ShaclConfig:
    include_labels: bool = True
    include_descriptions: bool = True


XSD_DATATYPES = {
    XSD.string, XSD.integer, XSD.int, XSD.long, XSD.short, XSD.byte,
    XSD.decimal, XSD.float, XSD.double, XSD.boolean, XSD.date, XSD.dateTime,
    XSD.time, XSD.duration, XSD.gYear, XSD.gMonth, XSD.gDay, XSD.gYearMonth,
    XSD.gMonthDay, XSD.anyURI, XSD.base64Binary, XSD.hexBinary,
    XSD.normalizedString, XSD.token, XSD.language, XSD.nonPositiveInteger,
    XSD.negativeInteger, XSD.nonNegativeInteger, XSD.positiveInteger,
    XSD.unsignedLong, XSD.unsignedInt, XSD.unsignedShort, XSD.unsignedByte,
}


class ConverterSelf:
    """Stand-in for the DomainRangeConverter instance: only what the region calls."""

    XSD_DATATYPES = XSD_DATATYPES

    def __eq__(self, other):
        return isinstance(other, ConverterSelf)

    def __hash__(self):
        return hash(ConverterSelf)

    def _is_datatype(self, uri: URIRef, graph: Graph) -> bool:
        if uri in self.XSD_DATATYPES:
            return True
        if (uri, RDF.type, RDFS.Datatype) in graph:
            return True
        return str(uri).startswith(str(XSD))
