# Extracted from RDFLib/pyLODE@0d0471fb99 : pylode/profiles/supermodel/query/__init__.py
# region: get_image_object (lines 118-135, band high)
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

def get_image_object(iri: URIRef, graph: Graph) -> ImageObject:
    name = get_value(iri, SDO.name, graph)
    description = get_value(iri, SDO.description, graph)
    encoding_format = get_value(iri, SDO.encodingFormat, graph)
    source = get_value(iri, DCTERMS.source, graph)
    order = get_value(iri, SH.order, graph)
    url = get_value(iri, SDO.contentUrl, graph)
    caption = get_value(iri, SDO.caption, graph)

    return ImageObject(
        name,
        description,
        encoding_format,
        source,
        order,
        url,
        caption,
    )
