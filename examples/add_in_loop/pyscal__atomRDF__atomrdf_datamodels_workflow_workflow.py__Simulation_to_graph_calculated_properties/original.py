# Extracted from pyscal/atomRDF@c9b070e15f : atomrdf/datamodels/workflow/workflow.py
# region: Simulation.to_graph_calculated_properties (lines 402-416, stratum add_in_loop)
# licence of the source repository: see meta.json
from rdflib import Graph, Namespace, XSD, RDF, RDFS, BNode, URIRef
from atomrdf_context import (
    CMSO,
    LDO,
    PLDO,
    PODO,
    CDCO,
    PROV,
    Literal,
    ASMO,
    MDO,
)

def to_graph_calculated_properties(self, graph, simulation):
    if self.calculated_property:
        for param in self.calculated_property:
            param_uri = param.to_graph(graph)
            graph.add((param_uri, ASMO.wasCalculatedBy, simulation))
            if param.associate_to_sample:
                for sample_id in param.associate_to_sample:
                    print(sample_id)
                    graph.add(
                        (
                            URIRef(sample_id),
                            ASMO.hasCalculatedProperty,
                            param_uri,
                        )
                    )
