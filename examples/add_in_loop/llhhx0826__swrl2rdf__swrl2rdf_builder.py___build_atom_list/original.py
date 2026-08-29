# Extracted from llhhx0826/swrl2rdf@190ffb3068 : swrl2rdf/builder.py
# region: _build_atom_list (lines 87-104, stratum add_in_loop)
# licence of the source repository: see meta.json
from typing import Dict, List, Optional
from rdflib import BNode, Graph, Literal, URIRef
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
SWRL_AtomList = SWRL.AtomList

def _build_atom_list(graph: Graph, atoms: List[Atom], prefix_map: PrefixMap) -> BNode:
    list_head = BNode()
    current = list_head
    for i, atom in enumerate(atoms):
        atom_node = _build_atom(graph, atom, prefix_map)
        graph.add((current, RDF.type, SWRL_AtomList))
        graph.add((current, RDF.first, atom_node))
        if i < len(atoms) - 1:
            rest = BNode()
            graph.add((current, RDF.rest, rest))
            current = rest
        else:
            graph.add((current, RDF.rest, RDF.nil))
    if not atoms:
        graph.add((list_head, RDF.type, SWRL_AtomList))
        graph.add((list_head, RDF.first, RDF.nil))
        graph.add((list_head, RDF.rest, RDF.nil))
    return list_head
