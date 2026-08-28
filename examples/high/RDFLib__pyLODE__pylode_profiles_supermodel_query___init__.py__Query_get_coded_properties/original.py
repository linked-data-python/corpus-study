# Extracted from RDFLib/pyLODE@0d0471fb99 : pylode/profiles/supermodel/query/__init__.py
# region: Query.get_coded_properties (lines 797-846, band high)
# licence of the source repository: see meta.json
from rdflib import Dataset, Graph, Literal, URIRef
from rdflib.graph import DATASET_DEFAULT_GRAPH_ID
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
from supermodel_model import (
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
from supermodel_common import (
    get_class,
    get_descriptions,
    get_is_defined_by,
    get_name,
    get_subclasses,
    get_values,
)

def get_coded_properties(
    self, cls_iri: URIRef, properties: dict[str, list[Property]]
) -> dict[str, list[Property]]:
    for prop in properties.copy():
        _graphs = list(
            filter(
                lambda g: g.identifier != DATASET_DEFAULT_GRAPH_ID,
                self.db.contexts((prop, RDF.type, QB.CodedProperty)),
            )
        )

        if _graphs:
            for _graph in _graphs:
                graph = self.db.get_graph(_graph.identifier)
                expected_value_iris = graph.objects(prop, RDFS.range)
                value_class_types = [
                    get_class(expected_value_iri, self.db, self.db, [])
                    for expected_value_iri in expected_value_iris
                ]

                name = get_name(prop, graph, self.db)
                description = (
                    get_descriptions(prop, graph)
                    or get_descriptions(prop, self.db)
                    or ""
                )

                new_prop = CodedProperty(
                    prop,
                    name,
                    description,
                    Profile(
                        graph.identifier,
                        get_name(graph.identifier, self.db),
                    ),
                    belongs_to_class=get_class(cls_iri, self.db, self.db, []),
                    value_class_types=value_class_types,
                    method="qb:CodedProperty",
                    codelist=[
                        Resource(
                            x,
                            get_name(x, graph),
                            get_descriptions(x, graph),
                        )
                        for x in graph.objects(prop, QB.codeList)
                    ],
                )
                properties[prop].append(new_prop)

    return properties
