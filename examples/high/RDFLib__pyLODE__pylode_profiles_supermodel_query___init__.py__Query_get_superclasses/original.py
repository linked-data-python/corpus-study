# Extracted from RDFLib/pyLODE@0d0471fb99 : pylode/profiles/supermodel/query/__init__.py
# region: Query.get_superclasses (lines 935-948, band high)
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
from supermodel_shim import (
    Class,
)

def get_superclasses(
    self, iri: URIRef, graph: Graph, ignored_classes: list[URIRef]
) -> list[Class]:
    superclasses = filter(
        lambda x: x not in ignored_classes and isinstance(x, URIRef),
        list(graph.objects(iri, RDFS.subClassOf)),
    )
    return sorted(
        [
            self.get_component_model_class(superclass, graph, ignored_classes)
            for superclass in superclasses
        ],
        key=lambda x: x.name,
    )
