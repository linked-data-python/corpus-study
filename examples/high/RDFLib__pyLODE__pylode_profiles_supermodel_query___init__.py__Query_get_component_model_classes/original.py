# Extracted from RDFLib/pyLODE@0d0471fb99 : pylode/profiles/supermodel/query/__init__.py
# region: Query.get_component_model_classes (lines 1028-1038, band high)
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
# context shim (see meta.json): the intra-package model module, vendored
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

def get_component_model_classes(
    self, graph: Graph, ignored_classes: list[URIRef]
) -> list[Class]:
    classes = graph.subjects(RDF.type, OWL.Class)

    result = []
    for c in filter(lambda x: x not in ignored_classes, classes):
        result.append(self.get_component_model_class(c, graph, ignored_classes))
        self.class_index.add(c)

    return sorted(result, key=lambda x: x.name)
