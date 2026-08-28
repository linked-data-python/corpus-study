# Extracted from llhhx0826/swrl2rdf@190ffb3068 : tests/test_builder.py
# region: test_class_atom_structure (lines 63-76, stratum trav_existence)
# licence of the source repository: see meta.json
from rdflib import BNode, Graph, URIRef
from rdflib.namespace import Namespace, RDF, RDFS
from swrl2rdf.builder import rules_to_graph
from swrl2rdf.model import ClassAtom, Rule, SameIndividualAtom, Variable
from swrl2rdf.prefixmap import PrefixMap
SWRL = Namespace("http://www.w3.org/2003/11/swrl#")
EX = "http://example.org/"

def test_class_atom_structure(prefix_map: PrefixMap) -> None:
    """ClassAtom must expose swrl:classPredicate and swrl:argument1."""
    g = Graph()
    rule = Rule(
        body=[ClassAtom(class_predicate=EX + "Person", argument=Variable("p"))],
        head=[ClassAtom(class_predicate=EX + "Adult", argument=Variable("p"))],
    )
    rules_to_graph([rule], prefix_map, g)
    class_atoms = list(g.subjects(RDF.type, SWRL.ClassAtom))
    assert len(class_atoms) >= 1
    atom = class_atoms[0]
    assert (atom, SWRL.classPredicate, URIRef(EX + "Person")) in g
    assert (atom, SWRL.argument1, None) is not True
    assert g.value(atom, SWRL.argument1) is not None
