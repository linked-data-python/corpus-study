# Extracted from Harold-Solbrig/funowl@69e1cbe2f6 : funowl/class_expressions.py
# region: ObjectMinCardinality.to_rdf (lines 254-269, stratum add_run_shared_subject)
# licence of the source repository: see meta.json
from rdflib import OWL, Graph, RDF
from rdflib.term import BNode

def to_rdf(self, g: Graph, emit_type_arc: bool = False) -> BNode:
    # _:x rdf:type owl:Restriction .
    # _:x owl:onProperty T(OPE) .
    # _:x owl:minCardinality "n"^^xsd:nonNegativeInteger .
    #
    # _:x owl:minQualifiedCardinality "n"^^xsd:nonNegativeInteger .
    # _:x owl:onClass T(CE) .
    x = BNode()
    g += [(x, RDF.type, OWL.Restriction), (x, OWL.onProperty, self.objectPropertyExpression.to_rdf(g))]
    g.add((x, OWL.minQualifiedCardinality if self.classExpression else OWL.minCardinality, self.min_.to_rdf(g)))
    if self.classExpression:
        g.add((x, OWL.onClass, self.classExpression.to_rdf(g)))
    return x
