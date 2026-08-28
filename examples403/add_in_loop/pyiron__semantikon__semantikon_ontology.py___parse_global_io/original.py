# Extracted from pyiron/semantikon@cfd1d3ffe5 : semantikon/ontology.py
# region: _parse_global_io (lines 967-989, stratum add_in_loop)
# licence of the source repository: see meta.json
from rdflib import OWL, RDF, RDFS, BNode, Graph, Literal, Namespace, URIRef
from semantikon.flowrep_to_networkx import (
    IO,
    Input,
    Node,
    Output,
    SemantikonDiGraph,
    _get_graph_hash,
    serialize_and_convert_to_networkx,
)
BASE: Namespace = Namespace("http://pyiron.org/ontology/")

def _parse_global_io(
    G: SemantikonDiGraph,
    workflow_node: URIRef,
    t_box: bool,
) -> Graph:
    g = _get_bound_graph()
    global_inputs: list[Input] = [
        n for n in G.nodes if G.in_degree(n) == 0 and isinstance(n, Input)
    ]
    global_outputs: list[Output] = [
        n for n in G.nodes if G.out_degree(n) == 0 and isinstance(n, Output)
    ]
    for io_list in (global_inputs, global_outputs):
        for io in io_list:
            if t_box:
                g += _to_owl_restriction(
                    workflow_node,
                    SNS.has_part,
                    BASE[G.t_ns + io],
                )
            else:
                g.add((workflow_node, SNS.has_part, BASE[G.a_ns + io]))
    return g
