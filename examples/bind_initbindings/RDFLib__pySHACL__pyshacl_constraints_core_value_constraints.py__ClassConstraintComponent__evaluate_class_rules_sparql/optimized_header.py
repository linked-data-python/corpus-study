# Extracted from RDFLib/pySHACL@469cca7a22 : pyshacl/constraints/core/value_constraints.py
# region: ClassConstraintComponent._evaluate_class_rules_sparql (lines 113-132, stratum bind_initbindings)
# licence of the source repository: see meta.json
from rdflib.term import Literal

def _evaluate_class_rules_sparql(self, target_graph, f_v_dict, class_rule):
    reports = []
    for f, value_nodes in f_v_dict.items():
        for v in value_nodes:
            if isinstance(v, Literal):
                self.shape.logger.debug(
                    "Class Constraint won't work with Literals. "
                    "Attempting to match Literal node {} to class of {} will fail.".format(v, class_rule)
                )
            elif target_graph.query("ASK {$value rdf:type/rdfs:subClassOf* $class .}",
                                    initBindings={"value": v, "class": class_rule}):
                continue
            reports.append(self.make_v_result(target_graph, f, value_node=v))
    return bool(reports), reports
