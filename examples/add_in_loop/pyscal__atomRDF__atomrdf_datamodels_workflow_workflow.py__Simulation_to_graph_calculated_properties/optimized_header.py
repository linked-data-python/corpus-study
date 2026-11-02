# Extracted from pyscal/atomRDF@c9b070e15f : atomrdf/datamodels/workflow/workflow.py
# region: Simulation.to_graph_calculated_properties (lines 402-416, stratum add_in_loop)
# licence of the source repository: see meta.json
from rdflib import URIRef
from atomrdf_context import ASMO

def to_graph_calculated_properties(self, graph, simulation):
    for param in self.calculated_property or []:
        param_uri = param.to_graph(graph)
        graph.add((param_uri, ASMO.wasCalculatedBy, simulation))
        for sample_id in param.associate_to_sample or []:
            print(sample_id)
            graph.add((URIRef(sample_id), ASMO.hasCalculatedProperty, param_uri))
