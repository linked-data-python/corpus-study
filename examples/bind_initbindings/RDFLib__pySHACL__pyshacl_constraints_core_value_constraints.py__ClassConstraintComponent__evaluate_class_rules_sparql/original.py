# Extracted from RDFLib/pySHACL@469cca7a22 : pyshacl/constraints/core/value_constraints.py
# region: ClassConstraintComponent._evaluate_class_rules_sparql (lines 113-132, stratum bind_initbindings)
# licence of the source repository: see meta.json
from rdflib.term import Literal, URIRef

def _evaluate_class_rules_sparql(self, target_graph, f_v_dict, class_rule):
    reports = []
    non_conformant = False
    sparql_ask = """ASK {$value rdf:type/rdfs:subClassOf* $class .}"""
    for f, value_nodes in f_v_dict.items():
        for v in value_nodes:
            found = False
            if isinstance(v, Literal):
                self.shape.logger.debug(
                    "Class Constraint won't work with Literals. "
                    "Attempting to match Literal node {} to class of {} will fail.".format(v, class_rule)
                )
            else:
                resp = target_graph.query(sparql_ask, initBindings={"value": v, "class": class_rule})
                found = resp.askAnswer
            if not found:
                non_conformant = True
                rept = self.make_v_result(target_graph, f, value_node=v)
                reports.append(rept)
    return non_conformant, reports
