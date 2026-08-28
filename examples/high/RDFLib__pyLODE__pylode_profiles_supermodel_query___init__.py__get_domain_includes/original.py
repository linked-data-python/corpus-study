# Extracted from RDFLib/pyLODE@0d0471fb99 : pylode/profiles/supermodel/query/__init__.py
# region: get_domain_includes (lines 226-233, band high)
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
from supermodel_query_common import (
    get_class,
    get_descriptions,
    get_is_defined_by,
    get_name,
    get_subclasses,
    get_values,
)

def get_domain_includes(iri: URIRef, graph: Graph, db: Dataset) -> list[Class]:
    domain_includes_iris = graph.objects(iri, SDO.domainIncludes)
    domain_includes = []
    for domain_includes_iri in domain_includes_iris:
        c = get_class(domain_includes_iri, graph, db, [])
        domain_includes.append(c)

    return domain_includes
