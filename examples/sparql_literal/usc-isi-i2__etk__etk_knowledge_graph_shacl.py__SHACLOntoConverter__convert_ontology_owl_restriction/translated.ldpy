# Extracted from usc-isi-i2/etk@2084003ae7 : etk/knowledge_graph/shacl.py
# region: SHACLOntoConverter._convert_ontology_owl_restriction (lines 152-185, stratum sparql_literal)
# licence of the source repository: see meta.json
from etk.knowledge_graph.node import URI, BNode, Literal, LiteralType

def _convert_ontology_owl_restriction(self):
    for c, p, exact, min_, max_ in self.onto_graph.query("""
      SELECT ?c ?p ?exact ?min ?max
      WHERE {
        ?c rdfs:subClassOf|owl:equivalentClass ?res .
        ?res a owl:Restriction ;
             owl:onProperty ?p .
        OPTIONAL {?res owl:cardinality ?exact}
        OPTIONAL {?res owl:minCardinality ?min}
        OPTIONAL {?res owl:maxCardinality ?max}
      }
    """):
        node_subject = self._class_shape(c)
        property_shape = self._property_shape(p)
        if exact:
            property_shape.add_property(URI('sh:count'), Literal(str(exact), type_=LiteralType.integer))
        if min_:
            property_shape.add_property(URI('sh:minCount'), Literal(str(min_), type_=LiteralType.integer))
        if max_:
            property_shape.add_property(URI('sh:maxCount'), Literal(str(max_), type_=LiteralType.integer))
        ranges = []
        for r, in self.onto_graph.query("""
          SELECT ?r
          WHERE {
            ?c rdfs:subClassOf|owl:equivalentClass ?res .
            ?res a owl:Restriction ;
                 owl:onProperty ?p ;
                 owl:allValuesFrom|owl:someValuesFrom|owl:hasValue ?r
          }
        """, initBindings={'c': c, 'p': p}):
            ranges.append(r)
        self._build_property_ranges(property_shape, ranges)
        node_subject.add_property(URI('sh:property'), property_shape)
        self._g.add_subject(node_subject)
