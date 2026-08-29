# Extracted from usc-isi-i2/etk@2084003ae7 : etk/knowledge_graph/shacl.py
# region: SHACLOntoConverter._convert_ontology_non_referenced_property (lines 103-118, stratum sparql_literal)
# licence of the source repository: see meta.json
from etk.knowledge_graph.node import URI, BNode, Literal, LiteralType

def _convert_ontology_non_referenced_property(self):
    for p, in self.onto_graph.query("""
      SELECT ?p
      WHERE {
        { ?p a rdfs:Property }
        UNION
        { ?p a owl:ObjectProperty }
        UNION
        { ?p a owl:DatatypeProperty }
        FILTER NOT EXISTS { ?p rdfs:domain ?c }
        FILTER NOT EXISTS { ?c owl:onProperty ?p }
      }
    """):
        p_shape = self._property_shape(p)
        p_shape.add_property(URI('rdf:type'), URI('sh:PropertyShape'))
        self._g.add_subject(p_shape)
