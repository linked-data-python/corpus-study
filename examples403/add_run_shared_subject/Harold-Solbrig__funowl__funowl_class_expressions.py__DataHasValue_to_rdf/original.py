# Extracted from Harold-Solbrig/funowl@69e1cbe2f6 : funowl/class_expressions.py
# region: DataHasValue.to_rdf (lines 410-418, stratum add_run_shared_subject)
# licence of the source repository: see meta.json
from rdflib import URIRef, OWL, Graph, RDF
from rdflib.term import BNode, Literal as RDFLiteral

def to_rdf(self, g: Graph, emit_type_arc: bool = False) -> BNode:
    # _:x rdf:type owl:Restriction .
    # _:x owl:onProperty T(DPE) .
    # _:x owl:hasValue T(lt) .
    x = BNode()
    g.add((x, RDF.type, OWL.Restriction))
    g.add((x, OWL.onProperty, self.dataPropertyExpression.to_rdf(g)))
    g.add((x, OWL.hasValue, self.literal.to_rdf(g)))
    return x
