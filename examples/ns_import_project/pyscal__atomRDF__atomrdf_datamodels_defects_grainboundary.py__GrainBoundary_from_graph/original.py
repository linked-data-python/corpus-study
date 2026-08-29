# Extracted from pyscal/atomRDF@c9b070e15f : atomrdf/datamodels/defects/grainboundary.py
# region: GrainBoundary.from_graph (lines 94-102, stratum ns_import_project)
# licence of the source repository: see meta.json
from rdflib import Graph, Namespace, XSD, RDF, RDFS, BNode, URIRef
from atomrdf.namespace import (
    CMSO,
    LDO,
    PLDO,
    PODO,
    CDCO,
    PROV,
    Literal,
    ASMO,
)
from atomrdf.utils import get_material

@classmethod
def from_graph(cls, graph, sample):
    material = get_material(graph, sample)
    for triple in graph.triples((material, CDCO.hasCrystallographicDefect, None)):
        plane_defect = triple[2]
        typev = graph.value(plane_defect, RDF.type)
        if typev is not None and typev == PLDO.GrainBoundary:
            return cls._read_gb(graph, sample, plane_defect)
    return None
