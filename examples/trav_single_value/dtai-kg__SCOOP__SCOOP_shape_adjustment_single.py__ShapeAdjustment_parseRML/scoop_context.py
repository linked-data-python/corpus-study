# Context shim (see meta.json): subset of SCOOP/shape_adjustment_single.py
# from dtai-kg/SCOOP@40c6fc0420, so the region executes outside the class.
# parseRML is a method: it reads the RML vocabulary constants set up by
# __init__ (LOGICAL_SOURCE, SUBJECT_MAP, POM, TRIPLES_MAP_CLASS, and the
# constants getSource/getSubjectMap/getPredicate/getObjectMap read in turn),
# and it calls those four sibling methods, none in the extracted region.
# All are copied VERBATIM from the pinned commit (none do I/O) so the
# fixture below exercises the real logic, not an invented approximation.
# Identical shim imported by both original.py and translated.ldpy.
import re

from rdflib import Namespace


class ShapeAdjustmentStub:
    def __init__(self, source_type="csv"):
        self.shaclNS = Namespace('http://www.w3.org/ns/shacl#')
        self.rdfSyntax = Namespace('http://www.w3.org/1999/02/22-rdf-syntax-ns#')
        self.rmlNS = Namespace('http://semweb.mmlab.be/ns/rml#')
        self.r2rmlNS = Namespace('http://www.w3.org/ns/r2rml#')
        self.QLNS = Namespace('http://semweb.mmlab.be/ns/ql#')
        self.FNMLNS = Namespace('http://semweb.mmlab.be/ns/fnml#')
        self.LOGICAL_SOURCE = self.rmlNS.logicalSource
        self.SOURCE = self.rmlNS.source
        self.REFERENCE_FORMULATION = self.rmlNS.referenceFormulation
        self.ITERATOR = self.rmlNS.iterator
        self.TEMPLATE = self.r2rmlNS.template
        self.REFERENCE = self.rmlNS.reference
        self.CLASS = self.r2rmlNS["class"]
        self.POM = self.r2rmlNS.predicateObjectMap
        self.PREDICATE = self.r2rmlNS.predicate
        self.PRED_MAP = self.r2rmlNS.predicateMap
        self.TRIPLES_MAP_CLASS = self.r2rmlNS.TriplesMap
        self.SUBJECT_MAP = self.r2rmlNS.subjectMap
        self.OBJECT_MAP = self.r2rmlNS.objectMap
        self.DATATYPE = self.r2rmlNS.datatype
        self.CONSTANT = self.r2rmlNS.constant
        self.OBJECT = self.r2rmlNS.object
        self.PARENTTM = self.rmlNS.parentTriplesMap
        self.source_type = source_type

    # --- verbatim from ShapeAdjustment at the pinned commit ---

    def getSource(self, source_identifier):
        source, reference_formulation, iterator = None, None, None
        for s, p, o in self.rml_graph:
            if s == source_identifier and p == self.SOURCE:
                source = re.sub(r'\[.*?\]', '', str(o))
            elif s == source_identifier and p == self.REFERENCE_FORMULATION:
                reference_formulation = o
            elif s == source_identifier and p == self.ITERATOR:
                iterator = re.sub(r'\[.*?\]', '', str(o))
        return source, reference_formulation, iterator

    def getSubjectMap(self, subject_map_identifier):
        path, classes, template_length, shared_key = [], [], None, None
        for s, p, o in self.rml_graph:
            if s == subject_map_identifier and p == self.TEMPLATE:
                path.extend(getattr(self, f"parseTemplate_{self.source_type}", None)(o))
                template_length = 0
                for i in str(o).split("{"):
                    template_length += len(i.split("}")[-1])
                shared_key = self.clean_shared_key(str(o))
            elif s == subject_map_identifier and p == self.REFERENCE:
                path.extend(getattr(self, f"parseReference_{self.source_type}", None)(o))
                shared_key = self.clean_shared_key(str(o))
            elif s == subject_map_identifier and p == self.CLASS:
                classes.append(o)
        return path, classes, template_length, shared_key

    def clean_shared_key(self, shared_key):
        shared_key = re.sub(r'parent::[^/]*\/', '', shared_key)
        shared_key = re.sub(r'{[^{]*?\[.*\]/', '{', shared_key)
        return shared_key

    def getPredicate(self, pom_identifier):
        for s, p, o in self.rml_graph:
            if s == pom_identifier and p == self.PREDICATE:
                return o
            elif s == pom_identifier and p == self.CONSTANT:
                return o
            elif s == pom_identifier and p == self.PRED_MAP:
                o = self.getPredicate(o)
                return o

    def getObjectMap(self, pom_identifier, parent=False):
        path, datatype, parent, template_length, constant, termType = [], None, False, None, False, None
        for s, p, o in self.rml_graph:
            if s == pom_identifier and p == self.OBJECT:
                path.append(o)
            elif s == pom_identifier and p == self.OBJECT_MAP:
                path, datatype, parent, template_length, constant, termType = self.getObjectMap(o)
            elif s == pom_identifier and p == self.DATATYPE:
                datatype = o
            elif s == pom_identifier and p == self.r2rmlNS.termType:
                termType = self.shaclNS[str(o).split("#")[-1]]
            elif s == pom_identifier and p == self.TEMPLATE:
                path.extend(getattr(self, f"parseTemplate_{self.source_type}", None)(o))
                template_length = 0
                for i in str(o).split("{"):
                    template_length += len(i.split("}")[-1])
                shared_key = str(o)
            elif s == pom_identifier and p == self.REFERENCE:
                path.extend(getattr(self, f"parseReference_{self.source_type}", None)(o))
                shared_key = str(o)
            elif s == pom_identifier and p == self.CONSTANT:
                path.append(o)
                constant = True
            elif s == pom_identifier and p == self.PARENTTM:
                path.append(o)
            elif s == pom_identifier and p == self.FNMLNS.functionValue:
                path = self.getFunctionValue(o)
                return path, datatype, parent, template_length, constant, termType
        return path, datatype, parent, template_length, constant, termType

    def getFunctionValue(self, function_identifier):
        path = []
        for s, p, o in self.rml_graph:
            if s == function_identifier and p == self.POM:
                path = self.getFunctionValue(o)
            elif s == function_identifier and p == self.OBJECT_MAP:
                path = self.getFunctionValue(o)
            elif s == function_identifier and p == self.REFERENCE:
                path.extend(getattr(self, f"parseReference_{self.source_type}", None)(o))
        return path

    def parseTemplate_csv(self, template):
        pattern = r'\{([^}]+)\}'
        matches = re.findall(pattern, template)
        matches = [self.iterator + "/" + i for i in matches]
        return [matches]

    def parseReference_csv(self, reference):
        pass
