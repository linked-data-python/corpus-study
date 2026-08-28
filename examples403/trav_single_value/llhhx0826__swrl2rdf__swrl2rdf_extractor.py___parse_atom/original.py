# Extracted from llhhx0826/swrl2rdf@190ffb3068 : swrl2rdf/extractor.py
# region: _parse_atom (lines 175-235, stratum trav_single_value)
# licence of the source repository: see meta.json
from typing import Dict, List, Optional, Set
from rdflib import BNode, Graph, Literal, URIRef
from rdflib.collection import Collection
from rdflib.namespace import Namespace, RDF, RDFS
from context_shim import (
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
    PrefixMap,
    SWRL,
    _display_iri,
    _term_from_node,
    _terms_from_arguments,
)
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

def _parse_atom(
    graph: Graph,
    atom_node: URIRef | BNode,
    prefix_map: PrefixMap,
    var_names: Dict[URIRef | BNode, str],
    reverse_mapping: Optional[Dict[str, str]],
) -> Optional[Atom]:
    types = list(graph.objects(atom_node, RDF.type))
    if SWRL_ClassAtom in types:
        cls = graph.value(atom_node, SWRL_classPredicate)
        arg1 = graph.value(atom_node, SWRL_argument1)
        return ClassAtom(
            class_predicate=_display_iri(cls, prefix_map, reverse_mapping),
            argument=_term_from_node(graph, arg1, prefix_map, var_names, reverse_mapping),
        )
    if SWRL_IndividualPropertyAtom in types:
        prop = graph.value(atom_node, SWRL_propertyPredicate)
        a1 = graph.value(atom_node, SWRL_argument1)
        a2 = graph.value(atom_node, SWRL_argument2)
        return IndividualPropertyAtom(
            property_predicate=_display_iri(prop, prefix_map, reverse_mapping),
            argument1=_term_from_node(graph, a1, prefix_map, var_names, reverse_mapping),
            argument2=_term_from_node(graph, a2, prefix_map, var_names, reverse_mapping),
        )
    if SWRL_DatavaluedPropertyAtom in types:
        prop = graph.value(atom_node, SWRL_propertyPredicate)
        a1 = graph.value(atom_node, SWRL_argument1)
        a2 = graph.value(atom_node, SWRL_argument2)
        return DatavaluedPropertyAtom(
            property_predicate=_display_iri(prop, prefix_map, reverse_mapping),
            argument1=_term_from_node(graph, a1, prefix_map, var_names, reverse_mapping),
            argument2=_term_from_node(graph, a2, prefix_map, var_names, reverse_mapping),
        )
    if SWRL_BuiltinAtom in types:
        builtin = graph.value(atom_node, SWRL_builtin)
        args_node = graph.value(atom_node, SWRL_arguments)
        terms: List[Term] = []
        if args_node is not None:
            try:
                coll = Collection(graph, args_node)
                terms = [
                    _term_from_node(graph, item, prefix_map, var_names, reverse_mapping)
                    for item in coll
                ]
            except Exception:
                pass
        return BuiltinAtom(
            builtin=_display_iri(builtin, prefix_map, reverse_mapping),
            arguments=terms,
        )
    if SWRL_SameIndividualAtom in types:
        terms = _terms_from_arguments(
            graph, atom_node, prefix_map, var_names, reverse_mapping
        )
        return SameIndividualAtom(arguments=terms)
    if SWRL_DifferentIndividualsAtom in types:
        terms = _terms_from_arguments(
            graph, atom_node, prefix_map, var_names, reverse_mapping
        )
        return DifferentIndividualsAtom(arguments=terms)
    return None
