"""Driver for semantikon `_wf_io_to_graph` (trav_existence).

The region builds a graph and, in the A-box branch, asks one existence
question of it: `g.value(data_node, SNS.has_value) is None` -- "does
data_node already have a value?" -- before writing `has_value`.  The graph
`g` is local and fresh, so the answer depends only on what the region wrote
a few lines earlier; the cases below are built so that it differs.

Real objects throughout: SemantikonDiGraph / Input / Output / Node from
semantikon 1.4.4, and the package's own helpers (`_get_bound_graph`,
`_to_owl_restriction`, `_translate_triples`, `SNS`).

  0 a-box, value + hash        guard true  -> has_value written
  1 a-box, node == data_node, has_specified_io = SNS.has_value
                               the region itself has just written
                               (data_node has_value data_node): guard FALSE,
                               the value is NOT written
  2 a-box, has_specified_io = SNS.has_value but node != data_node
                               (node has_value data_node): a neighbour that
                               must not match -- guard true, value written
                               (a pattern with the subject unbound, or the
                               object bound instead, would skip it)
  3 a-box, no "value"          nothing to guard
  4 a-box, triples + derived_from    translate_triples, and the list in `data`
                               is mutated by the region (append)
  5 t-box, hash                OWL restrictions, no existence test
  6 t-box, no hash
  7 a-box, a flat triple (not a list of triples)
"""
from rdflib import Literal, URIRef

from semantikon.flowrep_to_networkx import IO, Input, Node, Output, SemantikonDiGraph
from semantikon.ontology import BASE, SNS

from rdfeval.harness import run_pair

WF, ADD = Node("wf"), Node("add", owner=Node("wf"))
I_WF, I_ADD = Input(WF, "x"), Input(ADD, "a")
O_ADD, O_WF = Output(ADD, "output"), Output(WF, "y")
DATA = URIRef("http://example.org/data/d1")
OTHER = URIRef("http://example.org/data/other")


def _g():
    G = SemantikonDiGraph(prefix="Wf")
    G.add_node(WF)
    G.add_node(ADD)
    G.add_node(I_WF, position=0, value=3)
    G.add_node(I_ADD, position=0)
    G.add_node(O_ADD, position=0)
    G.add_node(O_WF, position=0)
    G.add_edge(I_WF, I_ADD)
    G.add_edge(I_ADD, ADD)
    G.add_edge(ADD, O_ADD)
    G.add_edge(O_ADD, O_WF)
    return G


def case(io, data, data_node=DATA, io_assignment=SNS.input_assignment,
         has_specified_io=SNS.has_participant, t_box=False, node_is_data=False):
    def make():
        G = _g()
        dn = data_node
        if node_is_data:                       # data_node == the io's own node
            dn = BASE[G.a_ns + io]
        return ((io, data, dn, G, io_assignment, has_specified_io, t_box), {})
    return make


VERDICT = run_pair(
    __file__,
    entry="_wf_io_to_graph",
    calls=[
        case(I_ADD, {"value": 3, "hash": "h@x"}),
        case(I_ADD, {"value": 3}, has_specified_io=SNS.has_value, node_is_data=True),
        case(I_ADD, {"value": 3}, has_specified_io=SNS.has_value),
        case(I_ADD, {"hash": "h@x"}),
        case(I_ADD, {"value": 2.5, "triples": [("self", SNS.denoted_by, OTHER)],
                     "derived_from": "inputs.a"}),
        case(I_ADD, {"value": 3, "hash": "h@x"}, t_box=True),
        case(I_ADD, {"value": 3}, t_box=True),
        case(I_ADD, {"triples": ("self", SNS.denoted_by, OTHER)}),
    ],
)
