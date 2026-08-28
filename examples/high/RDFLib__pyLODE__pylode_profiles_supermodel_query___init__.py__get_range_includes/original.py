# Extracted from RDFLib/pyLODE@0d0471fb99 : pylode/profiles/supermodel/query/__init__.py
# region: get_range_includes (lines 236-243, band high)
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

def get_range_includes(iri: URIRef, graph: Graph, db: Dataset) -> list[Class]:
    range_includes_iris = graph.objects(iri, SDO.rangeIncludes)
    range_includes = []
    for range_includes_iri in range_includes_iris:
        c = get_class(range_includes_iri, graph, db, [])
        range_includes.append(c)

    return range_includes
