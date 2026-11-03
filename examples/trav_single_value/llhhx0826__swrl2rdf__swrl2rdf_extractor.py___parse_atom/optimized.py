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
        return ClassAtom(
            class_predicate=_display_iri(
                graph.value(atom_node, SWRL_classPredicate), prefix_map, reverse_mapping),
            argument=_term_from_node(graph, graph.value(atom_node, SWRL_argument1),
                                     prefix_map, var_names, reverse_mapping),
        )
    for atom_type, atom_class in ((SWRL_IndividualPropertyAtom, IndividualPropertyAtom),
                                  (SWRL_DatavaluedPropertyAtom, DatavaluedPropertyAtom)):
        if atom_type in types:
            return atom_class(
                property_predicate=_display_iri(
                    graph.value(atom_node, SWRL_propertyPredicate), prefix_map, reverse_mapping),
                argument1=_term_from_node(graph, graph.value(atom_node, SWRL_argument1),
                                           prefix_map, var_names, reverse_mapping),
                argument2=_term_from_node(graph, graph.value(atom_node, SWRL_argument2),
                                           prefix_map, var_names, reverse_mapping),
            )
    if SWRL_BuiltinAtom in types:
        args_node = graph.value(atom_node, SWRL_arguments)
        terms: List[Term] = []
        if args_node is not None:
            try:
                terms = [
                    _term_from_node(graph, item, prefix_map, var_names, reverse_mapping)
                    for item in Collection(graph, args_node)
                ]
            except Exception:
                pass
        return BuiltinAtom(
            builtin=_display_iri(graph.value(atom_node, SWRL_builtin), prefix_map, reverse_mapping),
            arguments=terms,
        )
    for atom_type, atom_class in ((SWRL_SameIndividualAtom, SameIndividualAtom),
                                  (SWRL_DifferentIndividualsAtom, DifferentIndividualsAtom)):
        if atom_type in types:
            return atom_class(arguments=_terms_from_arguments(
                graph, atom_node, prefix_map, var_names, reverse_mapping))
    return None
