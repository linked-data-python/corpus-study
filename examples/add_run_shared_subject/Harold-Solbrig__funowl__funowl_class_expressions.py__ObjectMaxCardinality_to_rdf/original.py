# Extracted from Harold-Solbrig/funowl@69e1cbe2f6 : funowl/class_expressions.py
# region: ObjectMaxCardinality.to_rdf (lines 284-299, stratum add_run_shared_subject)
# licence of the source repository: see meta.json
from rdflib import URIRef, OWL, Graph, RDF
from rdflib.term import BNode, Literal as RDFLiteral

def to_rdf(self, g: Graph, emit_type_arc: bool = False) -> BNode:
    # _:x rdf:type owl:Restriction .
    # _:x owl:onProperty T(OPE) .
    # _:x owl:maxCardinality "n"^^xsd:nonNegativeInteger .
    #
    # _:x owl:maxQualifiedCardinality "n"^^xsd:nonNegativeInteger .
    # _:x owl:onClass T(CE) .
    x = BNode()
    g.add((x, RDF.type, OWL.Restriction))
    g.add((x, OWL.onProperty, self.objectPropertyExpression.to_rdf(g)))
    if self.classExpression:
        g.add((x, OWL.maxQualifiedCardinality, self.max_.to_rdf(g)))
        g.add((x, OWL.onClass, self.classExpression.to_rdf(g)))
    else:
        g.add((x, OWL.maxCardinality, self.max_.to_rdf(g)))
    return x
