# Extracted from RDFLib/pyLODE@0d0471fb99 : pylode/profiles/supermodel/query/__init__.py
# region: get_super_profiles (lines 315-326, band high)
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
from supermodel_shim import (  # context shim for pylode, see meta.json
    Class,
    ProfileHierarchyItem,
    get_name,
    get_values,
)

def get_super_profiles(iri: URIRef, graph: Graph) -> list[ProfileHierarchyItem]:
    super_profile_iris = graph.objects(iri, PROF.isProfileOf)
    super_profiles = []
    for super_profile_iri in super_profile_iris:
        super_profiles.append(
            ProfileHierarchyItem(
                iri=super_profile_iri,
                name=get_name(super_profile_iri, graph),
                is_profile_of=get_super_profiles(super_profile_iri, graph),
            )
        )
    return super_profiles
