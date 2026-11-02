# Extracted from MaximeJakubowski/sls_project@58f7d7840f : slsparser/shapels.py
# region: _target_parse (lines 158-208, stratum trav_existence)
# licence of the source repository: see meta.json
from rdflib import Graph
from rdflib import SH, RDF, RDFS
from rdflib.term import URIRef, Literal, BNode, Node
# `slsparser` is not installed: Op, SANode, PANode, POp and
# _extract_parameter_values come from a context shim, verbatim copies from the
# repository at the pinned commit (see meta.json).
from sls_context import Op, SANode, PANode, POp, _extract_parameter_values

def _target_parse(graph: Graph, shapename: Node) -> SANode:
    out = SANode(Op.OR, [])
    for tnode in _extract_parameter_values(graph, shapename, SH.targetNode):
        out.children.append(SANode(Op.HASVALUE, [tnode]))

    for tclass in _extract_parameter_values(graph, shapename, SH.targetClass):
        out.children.append(SANode(
            Op.COUNTRANGE,
            [
                Literal(1), None, PANode(POp.COMP, [
                    PANode(POp.PROP, [RDF.type]),
                    PANode(POp.KLEENE, [PANode(POp.PROP, [RDFS.subClassOf])])
                ]),
                SANode(Op.HASVALUE, [tclass])
            ]))

    if (shapename, RDF.type, RDFS.Class) in graph:
        out.children.append(SANode(
            Op.COUNTRANGE,
            [
                Literal(1), None, PANode(POp.COMP, [
                    PANode(POp.PROP, [RDF.type]),
                    PANode(POp.KLEENE, [PANode(POp.PROP, [RDFS.subClassOf])])
                ]),
                SANode(Op.HASVALUE, [shapename])
            ]))

    for tsub in _extract_parameter_values(graph, shapename,
                                          SH.targetSubjectsOf):
        out.children.append(SANode(Op.COUNTRANGE, [
            Literal(1),
            None,
            PANode(POp.PROP, [tsub]),
            SANode(Op.TOP, [])]))

    for tobj in _extract_parameter_values(graph, shapename,
                                          SH.targetObjectsOf):
        out.children.append(SANode(Op.COUNTRANGE, [
            Literal(1),
            None,
            PANode(POp.INV, [
                PANode(POp.PROP, [tobj])]),
            SANode(Op.TOP, [])]))

    if not out.children:
        out = SANode(Op.BOT, [])

    if out.op == Op.OR and len(out.children) == 1:
        return out.children[0]

    return out
