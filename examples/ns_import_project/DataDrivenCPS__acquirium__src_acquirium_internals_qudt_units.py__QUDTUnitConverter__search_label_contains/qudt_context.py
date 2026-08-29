# Context shim (see meta.json): stand-in for
# acquirium.internals.internals_namespaces (project namespaces, subset) from
# DataDrivenCPS/acquirium@e3bffb4bed8, plus the minimal QUDTUnitConverter/
# UnitDefinition machinery this region's own body calls (_looks_like_unit,
# _from_uri -> UnitDefinition.from_graph), so the region executes outside
# its package. Used identically by original.py, translated.ldpy AND
# driver.py -- the fixture-building `self` is built here once rather than
# duplicated on both sides, since ConverterStub needs no translation of its
# own (it is not part of the extracted region).
#
# QUDT/UNIT/QUDT_QUANTITY_KIND: real Namespace IRIs, transcribed verbatim
# from internals_namespaces.py.
#
# UnitDefinition: dataclass fields and from_graph() transcribed verbatim
# from qudt_units.py lines 72-133.
#
# ConverterStub._looks_like_unit / ._from_uri: transcribed verbatim from
# qudt_units.py lines 383-384 and 438-441, EXCEPT _from_uri's downstream
# FIXED_MULTIPLIERS lookup and call to self._refine_ratio_multiplier
# (qudt_units.py lines 442-453) -- refine_ratio_multiplier calls the
# public self.resolve_unit(...), which is reachable back into
# _search_label_contains itself (a different resolution strategy), so
# reproducing it would embark the whole converter, not just the one method
# under test. Both are downstream MULTIPLIER-ACCURACY refinements that do
# not change WHICH unit _search_label_contains finds -- irrelevant to this
# region's own contract -- and the fixture below deliberately uses units
# with plain (non-"-PER-") local names and multipliers, so neither branch
# is reachable. Not reached by this region or its fixture, left out, not
# simplified -- same reasoning as the johnjung/metadata_converters sibling
# of this stratum (MAPS/CHISOC, .triples()).
from dataclasses import dataclass, field

from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF

QUDT = Namespace("http://qudt.org/schema/qudt/")
UNIT = Namespace("http://qudt.org/vocab/unit/")
QUDT_QUANTITY_KIND = Namespace("http://qudt.org/vocab/quantitykind/")

__namespaces__ = {"qudt": QUDT}


class UnitNotFound(ValueError):
    """Raised when a unit URI is not present in the supplied graph (qudt_units.py line 64)."""


@dataclass(slots=True)
class UnitDefinition:
    """Minimal metadata needed to perform conversions."""

    uri: URIRef
    label: str | None
    symbol: str | None
    quantity_kind: URIRef | None
    multiplier: float
    offset: float
    dimension_vector: URIRef | None = None
    quantity_kinds: tuple = ()

    @classmethod
    def from_graph(cls, graph: Graph, uri: URIRef) -> "UnitDefinition":
        """Materialize a unit definition from the QUDT graph."""

        def _first_literal(subject, predicates):
            for predicate in predicates:
                lit = next(graph.objects(subject, predicate), None)
                if lit is not None:
                    return lit
            return None

        from rdflib.namespace import RDFS, SKOS

        quantity_kinds = list(graph.objects(uri, QUDT.QuantityKind))
        quantity_kinds += list(graph.objects(uri, QUDT.hasQuantityKind))
        seen_qk = set()
        unique_qks = []
        for qk in quantity_kinds:
            if isinstance(qk, URIRef) and qk not in seen_qk:
                seen_qk.add(qk)
                unique_qks.append(qk)

        preferred = QUDT_QUANTITY_KIND.Length
        if preferred in unique_qks:
            quantity_kind = preferred
        else:
            quantity_kind = unique_qks[0] if unique_qks else None

        dim_vec = next(graph.objects(uri, QUDT.hasDimensionVector), None)

        multiplier_lit = _first_literal(uri, (QUDT.conversionMultiplier,))
        offset_lit = _first_literal(uri, (QUDT.conversionOffset,))

        label_lit = _first_literal(uri, (RDFS.label, SKOS.prefLabel))
        symbol_lit = _first_literal(uri, (QUDT.symbol,))

        multiplier = float(multiplier_lit) if multiplier_lit is not None else 1.0
        offset = float(offset_lit) if offset_lit is not None else 0.0

        return cls(
            uri=uri,
            label=str(label_lit) if label_lit is not None else None,
            symbol=str(symbol_lit) if symbol_lit is not None else None,
            quantity_kind=quantity_kind if isinstance(quantity_kind, URIRef) else None,
            multiplier=multiplier,
            offset=offset,
            dimension_vector=dim_vec if isinstance(dim_vec, URIRef) else None,
            quantity_kinds=tuple(unique_qks),
        )


class ConverterStub:
    """Minimal stand-in for QUDTUnitConverter: only `.graph` and the two
    helper methods this region's own body calls."""

    def __init__(self, graph):
        self.graph = graph

    def _looks_like_unit(self, subject: URIRef) -> bool:
        return (subject, RDF.type, QUDT.Unit) in self.graph or (subject, QUDT.conversionMultiplier, None) in self.graph

    def _from_uri(self, uri: URIRef) -> UnitDefinition:
        if (uri, None, None) not in self.graph:
            raise UnitNotFound(f"Unit URI '{uri}' not present in provided QUDT graph")
        return UnitDefinition.from_graph(self.graph, uri)
