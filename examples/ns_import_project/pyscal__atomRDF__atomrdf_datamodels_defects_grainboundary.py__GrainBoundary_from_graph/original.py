# Extracted from pyscal/atomRDF@c9b070e15f : atomrdf/datamodels/defects/grainboundary.py
# region: GrainBoundary.from_graph (lines 94-102, stratum ns_import_project)
# licence of the source repository: see meta.json
from rdflib import Graph, Namespace, XSD, RDF, RDFS, BNode, URIRef
from atomrdf_context import (
    CMSO,
    PLDO,
    CDCO,
    get_material,
    GrainBoundary,
)

@classmethod
def from_graph(cls, graph, sample):
    material = get_material(graph, sample)
    for triple in graph.triples((material, CDCO.hasCrystallographicDefect, None)):
        plane_defect = triple[2]
        typev = graph.value(plane_defect, RDF.type)
        if typev is not None and typev == PLDO.GrainBoundary:
            return cls._read_gb(graph, sample, plane_defect)
    return None

# Restoring the binding (AGENT_BATCH's 163-regions case): after extraction
# `from_graph` is a bare @classmethod dangling outside any class -- its own
# body already works correctly through the ordinary classmethod protocol
# (unlike the johnjung/metadata_converters sibling in this stratum, `cls`
# here is genuinely GrainBoundary, matching to_graph's own usage a few lines
# above in the real file), it is only not yet attached to one. Attached to
# the shim's GrainBoundary (subset of grainboundary.py, see
# atomrdf_context.py) via the classmethod's own wrapped function, without
# altering the region's own decorator or body.
GrainBoundary.from_graph = classmethod(from_graph.__func__)


# Demo harness (identical on both sides, see meta.json): calls the real
# GrainBoundary.from_graph through the ordinary classmethod protocol and
# returns a plain dict, so the two sides' pydantic model instances (two
# distinct classes, one per exec'd module) compare by value rather than by
# identity.
def demo(graph, sample):
    result = GrainBoundary.from_graph(graph, sample)
    return result.model_dump() if result is not None else None
