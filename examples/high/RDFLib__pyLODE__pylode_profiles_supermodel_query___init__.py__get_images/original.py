# Extracted from RDFLib/pyLODE@0d0471fb99 : pylode/profiles/supermodel/query/__init__.py
# region: get_images (lines 138-169, band high)
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
from pylode.profiles.supermodel.query.common import (
    get_class,
    get_descriptions,
    get_is_defined_by,
    get_name,
    get_subclasses,
    get_values,
)

def get_images(iri: URIRef, graph: Graph) -> list[ImageObject]:
    """Get images from a subject in the graph.

    Example data:
    ```
    container:CSD
      schema:workExample [
        a schema:ImageObject ;
        schema:caption "Diagram for Cadastral Survey Dataset." ;
        schema:contentUrl "https://icsm-au.github.io/3d-csdm-design/2022/spec_files/CSD_logical.png"^^xsd:anyURI ;
        sh:order 0 ;
      ] ;
    .
    ```
    """
    images = []
    image_ids = graph.objects(iri, SDO.image)

    for image_id in image_ids:
        name = graph.value(image_id, SDO.name)
        description = get_descriptions(image_id, graph)
        encoding_format = graph.value(image_id, SDO.encodingFormat)
        source = graph.value(image_id, DCTERMS.source)
        caption = graph.value(image_id, SDO.caption)
        url = graph.value(image_id, SDO.contentUrl)
        order = graph.value(image_id, SH.order)

        images.append(
            ImageObject(name, description, encoding_format, source, caption, url, order)
        )

    return sorted(set(images), key=lambda x: x.order)
