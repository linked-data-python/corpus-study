# Extracted from dtai-kg/SCOOP@40c6fc0420 : SCOOP/shape_adjustment_single.py
# region: ShapeAdjustment.adjust_pom (lines 427-506, stratum add_run_shared_subject)
# licence of the source repository: see meta.json
from rdflib import Graph, URIRef, Literal, Namespace, BNode
from rdflib.namespace import RDF, RDFS, XSD, OWL

def adjust_pom(self, pom_list):
    if self.findNS == []:
        return None  # Comment it and next one if you want to add targetSubjectsOf to the shape which doesn't referenced by a node shape that has target declaration
    for pom in pom_list:
        for path_list in pom["path"]:
            if len(path_list) == 1:
                path = path_list[0]
                for shape_identifier in self.shape_path:
                    if "NodeShape" in shape_identifier:
                        continue 
                    for initial_path in self.shape_path[shape_identifier]:   
                        if (initial_path == path) or path.endswith(initial_path) or (pom["constant"] == True and initial_path == self.iterator) or ("parent:" in path and self.validatePath(path, initial_path)):
                            shape_identifier = URIRef(shape_identifier)
                            if shape_identifier in self.adjusted_shape:
                                # new_shape_identifier = shape_identifier + "/" + pom["property"].split("/")[-1]
                                new_shape_identifier = URIRef(str(shape_identifier) + "/" + pom["property"].split("/")[-1] + str(self.random_number.pop()))
                                self.updateShape(shape_identifier, new_shape_identifier)
                                shape_identifier = new_shape_identifier
                            self.adjusted_shape.append(shape_identifier)
                            self.initial_graph.remove((shape_identifier, self.shaclNS.path, None))
                            self.initial_graph.add((shape_identifier, self.shaclNS.path, pom["property"]))
                            if pom["datatype"] is not None:
                                self.initial_graph.remove((shape_identifier, self.shaclNS.nodeKind, None))
                                self.initial_graph.remove((shape_identifier, self.shaclNS.datatype, None))
                                self.initial_graph.add((shape_identifier, self.shaclNS.datatype, pom["datatype"]))
                            if pom["termType"] is not None:
                                self.initial_graph.remove((shape_identifier, self.shaclNS.nodeKind, None))
                                self.initial_graph.add((shape_identifier, self.shaclNS.nodeKind, pom["termType"]))
                            if pom["template_length"] is not None:
                                value = self.initial_graph.value(shape_identifier, self.shaclNS.minLength)
                                if value is not None:
                                    self.initial_graph.remove((shape_identifier, self.shaclNS.minLength, value))
                                    self.initial_graph.add((shape_identifier, self.shaclNS.minLength, Literal(int(pom["template_length"])+int(value))))
                                value = self.initial_graph.value(shape_identifier, self.shaclNS.maxLength)
                                if value is not None:
                                    self.initial_graph.remove((shape_identifier, self.shaclNS.maxLength, value))
                                    self.initial_graph.add((shape_identifier, self.shaclNS.maxLength, Literal(int(pom["template_length"])+int(value))))
                            # if self.findNS == []:
                            #     self.initial_graph.add((shape_identifier, self.shaclNS.targetSubjectsOf, pom["property"]))
                            self.findPS.append(shape_identifier)
                            for subject in self.findNS:
                                self.initial_graph.add((subject, self.shaclNS.property, shape_identifier))

            else:
                constraints = {}
                for path in path_list:
                    for shape_identifier_temp in self.shape_path:
                        if "NodeShape" in shape_identifier_temp:
                            continue
                        for initial_path in self.shape_path[shape_identifier_temp]:
                            if (initial_path == path) or path.endswith(initial_path) or (pom["constant"] == True and initial_path == self.iterator) or ("parent:" in path and self.validatePath(path, initial_path)):
                            #if initial_path == path or path.endswith(initial_path) or ("parent:" in path and self.validatePath(path, initial_path)):
                                shape_identifier = shape_identifier_temp
                                constraints = self.getConstraints(URIRef(shape_identifier_temp), constraints)
                if constraints!={}:
                    # new_shape_identifier = shape_identifier + "/" + pom["property"].split("/")[-1]     
                    shape_identifier = shape_identifier + "/" + pom["property"].split("/")[-1] + str(self.random_number.pop())
                    self.adjusted_shape.append(URIRef(shape_identifier))
                    self.updateCombinationShape(URIRef(shape_identifier), pom["property"], constraints,pom["template_length"])
                    self.findPS.append(URIRef(shape_identifier))

        if self.findPS == []:
            # shape_identifier = URIRef("http://example.com/PropertyShape/" + pom["property"].split("/")[-1])
            shape_identifier = URIRef("http://example.com/PropertyShape/" + pom["property"].split("/")[-1] + str(self.random_number.pop()))

            self.initial_graph.add((shape_identifier, RDF.type, self.shaclNS.PropertyShape))
            self.initial_graph.add((shape_identifier, self.shaclNS.path, pom["property"]))
            for subject in self.findNS:
                self.initial_graph.add((subject, self.shaclNS.property, shape_identifier))
            else:
                self.initial_graph.add((shape_identifier, self.shaclNS.targetObjectsOf, pom["property"]))
            if pom["datatype"] is not None:
                self.initial_graph.add((shape_identifier, self.shaclNS.datatype, pom["datatype"]))
            if pom["termType"] is not None:
                self.initial_graph.add((shape_identifier, self.shaclNS.nodeKind, pom["termType"]))

            self.findPS.append(shape_identifier)
            self.adjusted_shape.append(shape_identifier)

        self.findPS = []
