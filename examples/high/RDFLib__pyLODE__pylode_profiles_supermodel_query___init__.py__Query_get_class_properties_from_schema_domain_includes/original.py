# Extracted from RDFLib/pyLODE@0d0471fb99 : pylode/profiles/supermodel/query/__init__.py
# region: Query.get_class_properties_from_schema_domain_includes (lines 762-795, band high)
# licence of the source repository: see meta.json
from rdflib import Dataset, Graph, Literal, URIRef
from rdflib.namespace import (
    DC,
    DCTERMS,
    FOAF,
    ORG,
    OWL,
    PROF,
    PROV,
    QB,
    RDF,
    RDFS,
    SDO,
    SH,
    SKOS,
    VANN,
)
# context shim (see meta.json): pyLODE is not installed here; the model
# dataclasses and query helpers live in a local module -- identical for both
# representations.
from context import (
    Class,
    CodedProperty,
    ComponentModel,
    ImageObject,
    MediaObject,
    Note,
    Profile,
    ProfileHierarchyItem,
    ProfileType,
    Property,
    RDFProperty,
    Resource,
    SimpleCodedProperty,
    TextObject,
)
from context import (
    get_class,
    get_descriptions,
    get_is_defined_by,
    get_name,
    get_subclasses,
    get_values,
)

def get_class_properties_from_schema_domain_includes(
    self,
    iri: URIRef,
    properties: dict[URIRef, list[Property]],
    ignored_classes: list[URIRef],
) -> list[Property]:
    for _graph in self.db.graphs():
        graph = self.db.get_graph(_graph.identifier)

        schema_domain_includes_iris = graph.subjects(SDO.domainIncludes, iri)
        for schema_domain_includes_iri in schema_domain_includes_iris:
            name = get_name(schema_domain_includes_iri, graph)
            description = get_descriptions(schema_domain_includes_iri, graph)
            value_class_types = [
                get_class(c, graph, self.db, ignored_classes)
                for c in get_values(
                    schema_domain_includes_iri, graph, [SDO.rangeIncludes]
                )
            ]

            properties[schema_domain_includes_iri].append(
                Property(
                    iri=schema_domain_includes_iri,
                    name=name,
                    description=description,
                    profile=Profile(
                        graph.identifier,
                        get_name(graph.identifier, self.db),
                    ),
                    value_class_types=value_class_types,
                )
            )

    return properties
