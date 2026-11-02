# Extracted from usc-isi-i2/kgtk@b8d946b423 : kgtk/knowledge_graph/shacl.py
# region: SHACLOntoConverter._convert_ontology_owl_restriction (lines 151-184, stratum bind_initbindings)
# licence of the source repository: see meta.json
from shim import URI, Literal, LiteralType

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
        for predicate, value in (('sh:count', exact), ('sh:minCount', min_), ('sh:maxCount', max_)):
            if value:
                property_shape.add_property(
                    URI(predicate), Literal(str(value), type_=LiteralType.integer))
        self._build_property_ranges(property_shape, [r for r, in self.onto_graph.query("""
          SELECT ?r
          WHERE {
            ?c rdfs:subClassOf|owl:equivalentClass ?res .
            ?res a owl:Restriction ;
                 owl:onProperty ?p ;
                 owl:allValuesFrom|owl:someValuesFrom|owl:hasValue ?r
          }
        """, initBindings={'c': c, 'p': p})])
        node_subject.add_property(URI('sh:property'), property_shape)
        self._g.add_subject(node_subject)
