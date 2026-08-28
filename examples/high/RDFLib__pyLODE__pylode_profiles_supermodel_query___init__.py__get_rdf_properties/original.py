# Extracted from RDFLib/pyLODE@0d0471fb99 : pylode/profiles/supermodel/query/__init__.py
# region: get_rdf_properties (lines 276-290, band high)
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
from pylode.profiles.supermodel.model import (
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
from pylode.rdf_elements import (
    AGENT_PROPS,
    OBJECT_PROPERTY_SUBCLASSES,
    ONTOLOGY_PROPS,
    ONTPUB,
)

def get_rdf_properties(
    rdf_property_type: URIRef, graph: Graph, db: Dataset
) -> list[RDFProperty]:
    property_iris = set(graph.subjects(RDF.type, rdf_property_type))
    if rdf_property_type == OWL.ObjectProperty:
        # OWL 2 declares these to be subclasses of owl:ObjectProperty
        for prop_type in OBJECT_PROPERTY_SUBCLASSES:
            property_iris.update(graph.subjects(RDF.type, prop_type))
    properties = []
    for property_iri in property_iris:
        prop = get_rdf_property(property_iri, graph, db)

        properties.append(prop)

    return sorted(properties, key=lambda x: x.name)
