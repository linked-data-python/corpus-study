# Context shim (see meta.json): stands in for the dtai-kg/SCOOP
# ShapeAdjustment instance that adjust_pom reads/writes through self
# (SCOOP/shape_adjustment_single.py, dtai-kg/SCOOP@40c6fc0420).
#
# adjust_pom calls four sibling methods that are not in the extracted
# region: validatePath, updateShape, getConstraints and
# updateCombinationShape. None of them do I/O (no input(), no network); all
# four are copied VERBATIM from the pinned commit (lines 409-412 and
# 508-533) so the fixtures in driver.py exercise the real logic, not an
# invented approximation.
#
# ShapeAdjustmentStub carries only the constructor state adjust_pom and
# those four methods actually read: shaclNS, random_number, findNS, findPS,
# shape_path, iterator, adjusted_shape, initial_graph -- not the rest of the
# real ShapeAdjustment (RML parsing, source_type, adjusted_graph, the
# shared_sm_identifier bookkeeping used by the sibling adjust_sm method),
# which this region never touches. Identical shim imported by both
# original.py and translated.ldpy.
from rdflib import Literal, Namespace
from rdflib.namespace import RDF


class ShapeAdjustmentStub:
    def __init__(self, initial_graph, shape_path, findNS, iterator=""):
        self.shaclNS = Namespace('http://www.w3.org/ns/shacl#')
        self.initial_graph = initial_graph
        self.shape_path = shape_path
        self.findNS = findNS
        self.findPS = []
        self.adjusted_shape = []
        self.iterator = iterator
        # Deterministic stand-in for the real constructor's
        # `[random.randint(1000, 9999) for i in range(3000)]`: adjust_pom
        # only ever calls .pop() (from the end), so a fixed sequence keeps
        # both sides' output identical without depending on the RNG.
        self.random_number = list(range(9000, 9100))

    # --- verbatim from ShapeAdjustment at the pinned commit ---

    def validatePath(self, path_target, path):
        result = path_target.split("parent::")
        final_result = []
        for item in result:
            final_result.extend(item.split("*"))
        final_result = [i for i in final_result if i != ""]
        if path.endswith(final_result[-1]):
            for p in final_result[:-1]:
                if p not in path:
                    return False
            return True
        else:
            return False

    def updateShape(self, shape_identifier, new_shape_identifier):
        for s, p, o in self.initial_graph.triples((shape_identifier, None, None)):
            self.initial_graph.add((new_shape_identifier, p, o))
        for s, p, o in self.initial_graph.triples((None, None, shape_identifier)):
            self.initial_graph.add((s, p, new_shape_identifier))

    def getConstraints(self, shape_identifier, constraints):
        for s, p, o in self.initial_graph.triples((shape_identifier, None, None)):
            if p != RDF.type:
                l = constraints.get(p, [])
                l.append(o)
                constraints[p] = l
        return constraints

    def updateCombinationShape(self, shape_identifier, property, constraints, template_length):
        self.initial_graph.add((shape_identifier, RDF.type, self.shaclNS.PropertyShape))
        self.initial_graph.add((shape_identifier, self.shaclNS.nodeKind, self.shaclNS.IRI))
        self.initial_graph.add((shape_identifier, self.shaclNS.path, property))

        for subject in self.findNS:
            self.initial_graph.add((subject, self.shaclNS.property, shape_identifier))
        else:
            self.initial_graph.add((shape_identifier, self.shaclNS.targetObjectsOf, property))

        for constraint, constraint_value in constraints.items():
            if constraint == self.shaclNS.minCount or constraint == self.shaclNS.maxCount:
                current_number = 1
                for value in constraint_value:
                    current_number *= int(value)
                self.initial_graph.add((shape_identifier, constraint, Literal(current_number)))
            elif constraint == self.shaclNS.minLength or constraint == self.shaclNS.maxLength:
                current_number = template_length
                for value in constraint_value:
                    current_number += int(value)
                self.initial_graph.add((shape_identifier, constraint, Literal(current_number)))
