# Extracted from pyscal/atomRDF@c9b070e15f : atomrdf/datamodels/structure.py
# region: AtomicScaleSample.to_graph_calculated_properties (lines 704-714, stratum ns_import_project)
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
    DCAT,
)

def to_graph_calculated_properties(self, graph):
    if self.calculated_property:
        for param in self.calculated_property:
            param_uri = param.to_graph(graph)
            graph.add(
                (
                    URIRef(self.id),
                    ASMO.hasCalculatedProperty,
                    param_uri,
                )
            )
