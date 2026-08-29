# Extracted from llhhx0826/swrl2rdf@190ffb3068 : swrl2rdf/builder.py
# region: _build_atom (lines 107-170, stratum add_run_shared_subject)
# licence of the source repository: see meta.json
from typing import Dict, List, Optional
from rdflib import BNode, Graph, Literal, URIRef
from rdflib.collection import Collection
from rdflib.namespace import Namespace, RDF, RDFS, XSD
from swrl2rdf.model import (
    Atom,
    BuiltinAtom,
    ClassAtom,
    DatavaluedPropertyAtom,
    DifferentIndividualsAtom,
    IndividualPropertyAtom,
    IRITerm,
    LiteralTerm,
    Rule,
    SameIndividualAtom,
    Term,
    Variable,
)
from swrl2rdf.prefixmap import PrefixMap
SWRL_ClassAtom = SWRL.ClassAtom
SWRL_IndividualPropertyAtom = SWRL.IndividualPropertyAtom
SWRL_DatavaluedPropertyAtom = SWRL.DatavaluedPropertyAtom
SWRL_BuiltinAtom = SWRL.BuiltinAtom
SWRL_SameIndividualAtom = SWRL.SameIndividualAtom
SWRL_DifferentIndividualsAtom = SWRL.DifferentIndividualsAtom
SWRL_classPredicate = SWRL.classPredicate
SWRL_propertyPredicate = SWRL.propertyPredicate
SWRL_argument1 = SWRL.argument1
SWRL_argument2 = SWRL.argument2
SWRL_arguments = SWRL.arguments
SWRL_builtin = SWRL.builtin

def _build_atom(graph: Graph, atom: Atom, prefix_map: PrefixMap) -> BNode:
    node = BNode()
    var_map: Dict[str, BNode] = {}

    if isinstance(atom, ClassAtom):
        graph.add((node, RDF.type, SWRL_ClassAtom))
        graph.add(
            (node, SWRL_classPredicate, _predicate_ref(atom.class_predicate, prefix_map))
        )
        graph.add(
            (node, SWRL_argument1, _term_node(graph, atom.argument, prefix_map, var_map))
        )

    elif isinstance(atom, IndividualPropertyAtom):
        graph.add((node, RDF.type, SWRL_IndividualPropertyAtom))
        graph.add(
            (
                node,
                SWRL_propertyPredicate,
                _predicate_ref(atom.property_predicate, prefix_map),
            )
        )
        graph.add(
            (node, SWRL_argument1, _term_node(graph, atom.argument1, prefix_map, var_map))
        )
        graph.add(
            (node, SWRL_argument2, _term_node(graph, atom.argument2, prefix_map, var_map))
        )

    elif isinstance(atom, DatavaluedPropertyAtom):
        graph.add((node, RDF.type, SWRL_DatavaluedPropertyAtom))
        graph.add(
            (
                node,
                SWRL_propertyPredicate,
                _predicate_ref(atom.property_predicate, prefix_map),
            )
        )
        graph.add(
            (node, SWRL_argument1, _term_node(graph, atom.argument1, prefix_map, var_map))
        )
        graph.add(
            (node, SWRL_argument2, _term_node(graph, atom.argument2, prefix_map, var_map))
        )

    elif isinstance(atom, BuiltinAtom):
        graph.add((node, RDF.type, SWRL_BuiltinAtom))
        graph.add((node, SWRL_builtin, _predicate_ref(atom.builtin, prefix_map)))
        arg_nodes = [
            _term_node(graph, t, prefix_map, var_map) for t in atom.arguments
        ]
        args_bnode = BNode()
        Collection(graph, args_bnode, arg_nodes)
        graph.add((node, SWRL_arguments, args_bnode))

    elif isinstance(atom, SameIndividualAtom):
        graph.add((node, RDF.type, SWRL_SameIndividualAtom))
        _add_multi_arguments(graph, node, atom.arguments, prefix_map, var_map)

    elif isinstance(atom, DifferentIndividualsAtom):
        graph.add((node, RDF.type, SWRL_DifferentIndividualsAtom))
        _add_multi_arguments(graph, node, atom.arguments, prefix_map, var_map)

    return node
