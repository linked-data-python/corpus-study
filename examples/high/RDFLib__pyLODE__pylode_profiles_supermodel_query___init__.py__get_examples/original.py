# Extracted from RDFLib/pyLODE@0d0471fb99 : pylode/profiles/supermodel/query/__init__.py
# region: get_examples (lines 83-99, band high)
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

def get_examples(iri: URIRef, graph: Graph) -> list[MediaObject]:
    example_iris = graph.objects(iri, SDO.workExample)
    examples = []
    for example_iri in example_iris:
        class_types = list(graph.objects(example_iri, RDF.type))
        if SDO.TextObject in class_types:
            text_object = get_text_object(example_iri, graph)
            examples.append(text_object)
        elif SDO.ImageObject in class_types:
            image_object = get_image_object(example_iri, graph)
            examples.append(image_object)
        else:
            raise ValueError(
                f"Examples must be either an sdo:TextObject or an sdo:ImageObject."
            )

    return sorted(examples, key=lambda x: x.order)
