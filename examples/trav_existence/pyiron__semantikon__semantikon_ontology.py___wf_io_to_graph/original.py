# Extracted from pyiron/semantikon@cfd1d3ffe5 : semantikon/ontology.py
# region: _wf_io_to_graph (lines 885-937, stratum trav_existence)
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

def _wf_io_to_graph(
    node_name: IO,
    data: dict,
    data_node: URIRef,
    G: SemantikonDiGraph,
    io_assignment: URIRef,
    has_specified_io: URIRef,
    t_box: bool,
) -> Graph:
    node = BASE[G.t_ns + node_name] if t_box else BASE[G.a_ns + node_name]
    g = _get_bound_graph()
    g.add((node, SNS.local_identifier, Literal(node_name.port)))
    if t_box:
        g += _to_owl_restriction(node, has_specified_io, data_node)
        g.add((node, RDFS.label, Literal(str(node_name))))
        g.add((node, RDFS.subClassOf, io_assignment))
        g.add((data_node, RDFS.subClassOf, SNS.value_specification))
        if "hash" in data:
            g += _to_owl_restriction(data_node, SNS.denoted_by, SNS.identifier)
    else:
        data_node_name = G._get_data_node(io=node_name)
        g.add((data_node, RDF.type, BASE[G.t_ns + data_node_name]))
        g.add(
            (
                data_node,
                RDFS.label,
                Literal(G.a_ns_short + data_node_name),
            )
        )
        g.add((node, RDFS.label, Literal(G.a_ns_short + str(node_name))))
        g.add((node, has_specified_io, data_node))
        if "value" in data and g.value(data_node, SNS.has_value) is None:
            g.add((data_node, SNS.has_value, Literal(data["value"])))
        if "hash" in data:
            hash_bnode = BASE[G.a_ns + data_node_name + "_hash"]
            g.add((data_node, SNS.denoted_by, hash_bnode))
            g.add((hash_bnode, RDF.type, SNS.identifier))
            g.add((hash_bnode, SNS.has_value, Literal(data["hash"])))
            g.add((hash_bnode, RDFS.label, Literal(f"{G.a_ns_short}{node_name}_hash")))
    triples = data.get("triples", [])
    if triples != [] and not isinstance(triples[0], list | tuple):
        triples = [triples]
    if "derived_from" in data:
        triples.append(("self", SNS.derives_from, data["derived_from"]))
    if len(triples) > 0:
        g += _translate_triples(
            triples=triples,
            node_name=node_name,
            data_node=data_node,
            G=G,
            t_box=t_box,
        )
    return g
