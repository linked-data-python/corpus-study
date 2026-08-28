# Context shim (see meta.json): the part of brickschema.graph.Graph that the
# region uses, transcribed from BrickSchema/py-brickschema (corpus checkout
# BrickSchema__py-brickschema, brickschema/graph.py): the constructor binds
# the standard Brick prefixes, and `add` accepts a list of (predicate,
# object) pairs as the object of a triple, substituting a blank node.
# Identical for both representations.
import rdflib

from namespaces import BRICK, QUDT, QUDTDV, QUDTQK, RDFS, SKOS, UNIT, XSD

RDF = rdflib.RDF
OWL = rdflib.OWL


class Graph(rdflib.Graph):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bind("rdf", RDF)
        self.bind("owl", OWL)
        self.bind("rdfs", RDFS)
        self.bind("skos", SKOS)
        self.bind("xsd", XSD)
        self.bind("brick", BRICK)
        self.bind("qudt", QUDT)
        self.bind("qudtqk", QUDTQK)
        self.bind("qudtdv", QUDTDV)
        self.bind("unit", UNIT)

    def add(self, *triples):
        """brickschema.graph.Graph.add (verbatim behaviour).

        If the object of a triple is a list/tuple of length-2 items, a blank
        node is substituted as the object and the items are added as
        predicate/object pairs on that blank node.
        """
        for triple in triples:
            assert len(triple) == 3
            obj = triple[2]
            if isinstance(obj, (list, tuple)):
                for suffix in obj:
                    assert len(suffix) == 2
                bnode = rdflib.BNode()
                self.add((triple[0], triple[1], bnode))
                for (nested_pred, nested_obj) in obj:
                    self.add((bnode, nested_pred, nested_obj))
            else:
                super().add(triple)
