# Extracted from aigora-de/rdf-construct@670e400ea4 : src/rdf_construct/shacl/converters.py
# region: CardinalityConverter.convert_for_class (lines 309-409, stratum trav_navigation)
# licence of the source repository: see meta.json
from rdflib import BNode, Graph, RDF, RDFS, URIRef, OWL
from context_shim import PropertyConstraint  # context shim -- see meta.json

def convert_for_class(
    self,
    cls: URIRef,
    source_graph: Graph,
    config: "ShaclConfig",
) -> list[PropertyConstraint]:
    """Extract cardinality restrictions from class definition."""
    constraints: list[PropertyConstraint] = []

    # Find restrictions that this class is a subclass of
    for superclass in source_graph.objects(cls, RDFS.subClassOf):
        if not isinstance(superclass, BNode):
            continue

        # Check if it's an owl:Restriction
        if (superclass, RDF.type, OWL.Restriction) not in source_graph:
            continue

        on_prop = source_graph.value(superclass, OWL.onProperty)
        if not isinstance(on_prop, URIRef):
            continue

        constraint = PropertyConstraint(path=on_prop)
        has_constraint = False

        # Exact cardinality
        exact = source_graph.value(superclass, OWL.cardinality)
        if exact:
            constraint.min_count = constraint.max_count = int(exact)
            has_constraint = True

        # Minimum cardinality
        min_card = source_graph.value(superclass, OWL.minCardinality)
        if min_card:
            constraint.min_count = int(min_card)
            has_constraint = True

        # Maximum cardinality
        max_card = source_graph.value(superclass, OWL.maxCardinality)
        if max_card:
            constraint.max_count = int(max_card)
            has_constraint = True

        # Qualified cardinality
        qual_card = source_graph.value(superclass, OWL.qualifiedCardinality)
        if qual_card:
            constraint.min_count = constraint.max_count = int(qual_card)
            on_data = source_graph.value(superclass, OWL.onDataRange)
            if on_data:
                constraint.datatype = on_data
            has_constraint = True

        # Qualified min cardinality
        qual_min = source_graph.value(superclass, OWL.minQualifiedCardinality)
        if qual_min:
            constraint.min_count = int(qual_min)
            has_constraint = True

        # Qualified max cardinality
        qual_max = source_graph.value(superclass, OWL.maxQualifiedCardinality)
        if qual_max:
            constraint.max_count = int(qual_max)
            has_constraint = True

        # Also get the qualification
        on_class = source_graph.value(superclass, OWL.onClass)
        if on_class and (qual_card or qual_min or qual_max):
            constraint.node_class = on_class

        # someValuesFrom implies at least one value
        some_from = source_graph.value(superclass, OWL.someValuesFrom)
        if some_from:
            constraint.min_count = 1
            has_constraint = True

        # allValuesFrom constrains the type but not cardinality
        all_from = source_graph.value(superclass, OWL.allValuesFrom)
        for type_from in (some_from, all_from):
            if type_from and isinstance(type_from, URIRef):
                # Could be a class or datatype
                if self._is_datatype(type_from, source_graph):
                    constraint.datatype = type_from
                else:
                    constraint.node_class = type_from
                has_constraint = True

        if has_constraint:
            constraints.append(constraint)

    return constraints
