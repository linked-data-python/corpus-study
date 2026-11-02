# Context shim (see meta.json): subset of shapiro_model.py from
# mathiasrichter/shapiro@3954ef2148, so the region executes outside the
# package. ShaclProperty keeps the class attributes the ORIGINAL reads through
# `self` (the three prepared queries, verbatim, and get_node) but not
# get_constraints, which is the region. The translation inlines those query
# texts as s{ } islands and only uses self.get_node / self.iri / self.graph.
# Identical bindings for both representations.
from urllib.parse import urlparse

from rdflib import BNode, Graph, URIRef
from rdflib.plugins.sparql import prepareQuery


class ShaclConstraint:
    def __init__(self, parent, constraint_iri: str, value, is_enum: bool):
        self.parent = parent
        self.constraint_iri = constraint_iri
        self.value = value
        self.is_enum = is_enum


class ShaclProperty:
    SHACL_CONSTRAINTS_QUERY = prepareQuery(
        """ 
            SELECT DISTINCT ?property ?constraint ?value
            WHERE
            {
                {
                    ?property ?constraint ?value .
                    FILTER(STRSTARTS(STR(?constraint), "http://www.w3.org/ns/shacl#")) .
                }
            }    
        """
    )

    SHACL_IN_QUERY = prepareQuery(
        """
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                PREFIX sh: <http://www.w3.org/ns/shacl#>

                SELECT  ?source ?item
                WHERE {
                    ?source sh:in/rdf:rest*/rdf:first ?item
                }
            """
    )

    TRANSITIVE_SUPERPROPERTIES_QUERY = prepareQuery(
        """
        PREFIX rdfs:<http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT DISTINCT ?superproperty
        WHERE
        {
            {
                ?subproperty rdfs:subPropertyOf* ?superproperty .
            }
            UNION
            {
                ?subproperty sh:path ?property.
                ?property rdfs:subPropertyOf* ?superproperty .
            }
        }
        """
    )

    def __init__(self, iri: str, graph: Graph):
        self.iri = iri
        self.graph = graph

    def get_node(self, iri: str):
        if urlparse(iri).scheme == "":  #  if iri is a blank node
            return BNode(iri)
        else:
            return URIRef(iri)
