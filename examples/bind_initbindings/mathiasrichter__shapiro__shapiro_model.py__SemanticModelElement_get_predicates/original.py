# Extracted from mathiasrichter/shapiro@3954ef2148 : shapiro_model.py
# region: SemanticModelElement.get_predicates (lines 218-225, stratum bind_initbindings)
# licence of the source repository: see meta.json
from rdflib import Graph, URIRef, BNode

def get_predicates(self) -> dict:
    result = self.graph.query(
        self.PREDICATES_QUERY, initBindings={"subject": URIRef(self.iri)}
    )
    predicates = []
    for r in result:
        predicates.append(Predicate(str(r.predicate), self.graph, PredicateValue(str(r.object), self.graph)))
    return predicates
