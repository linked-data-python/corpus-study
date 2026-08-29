# Extracted from pyiron/semantikon@cfd1d3ffe5 : semantikon/ontology.py
# region: _wf_node_to_graph (lines 541-601, stratum add_run_shared_subject)
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

def _wf_node_to_graph(
    node_name: Node,
    data: dict,
    G: SemantikonDiGraph,
    t_box: bool,
) -> Graph:
    g = _get_bound_graph()
    if "function" in data:
        f_node = BASE[data["function"]["identifier"].replace(".", "-")]
        if list(g.triples((f_node, None, None))) == [] and t_box:
            g += _function_to_graph(
                f_node,
                data["function"],
                input_args=[
                    {"arg": item.port} | G.nodes[item]
                    for item in G.predecessors(node_name)
                ],
                output_args=[
                    {"arg": item.port} | G.nodes[item]
                    for item in G.successors(node_name)
                ],
                uri=data.get("uri"),
            )
    if t_box:
        node = BASE[G.t_ns + node_name]
        for io in [G.predecessors(node_name), G.successors(node_name)]:
            for item in io:
                g += _to_owl_restriction(
                    node,
                    SNS.has_part,
                    BASE[G.t_ns + item],
                )
        g.add((BASE[G.t_ns + node_name], RDFS.subClassOf, SNS.workflow_node))
        if "function" in data:
            g += _to_owl_restriction(
                node,
                SNS.concretizes,
                f_node,
                restriction_type=OWL.hasValue,
            )
        g.add((node, RDFS.label, Literal(str(node_name))))
        g.add((node, SNS.local_identifier, Literal(node_name.name)))
        if node_name.owner:
            g += _to_owl_restriction(
                BASE[G.t_ns + node_name.owner],
                SNS.has_part,
                node,
            )
    else:
        node = BASE[G.a_ns + node_name]
        g.add((node, RDF.type, BASE[G.t_ns + node_name]))
        g.add((node, RDFS.label, Literal(G.a_ns_short + str(node_name))))
        for inp in G.predecessors(node_name):
            g.add((node, SNS.has_part, BASE[G.a_ns + inp]))
        for out in G.successors(node_name):
            g.add((node, SNS.has_part, BASE[G.a_ns + out]))
        if "function" in data:
            g.add((node, SNS.concretizes, f_node))
        if node_name.owner:
            g.add((BASE[G.a_ns + node_name.owner], SNS.has_part, node))
    return g
