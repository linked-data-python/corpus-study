# Extracted from dtai-kg/SCOOP@40c6fc0420 : SCOOP/shape_integration_priority_r.py
# region: ShapeIntegrationPriorityR.conflictChecking (lines 242-357, stratum add_isolated)
# licence of the source repository: see meta.json
from rdflib import Graph, Namespace, URIRef, Literal, BNode

elif constraint_add == self.shaclNS.maxInclusive:
    if constraints_current.get(self.shaclNS.maxInclusive, None) != None:
        pass
    elif (constraints_current.get(self.shaclNS.nodeKind, None) == None) or "Literal" in str(constraints_current.get(self.shaclNS.nodeKind, None)):
        if (constraints_current.get(self.shaclNS.minExclusive, None) == None or constraint_add_value > constraints_current.get(self.shaclNS.minExclusive, None)) and (constraints_current.get(self.shaclNS.minInclusive, None) == None or constraint_add_value >= constraints_current.get(self.shaclNS.minInclusive, None)):
            if "string" not in str(constraints_current.get(self.shaclNS.datatype, None)):
                self.SHACL.add((identifier_path_current, constraint_add, constraint_add_value))

elif constraint_add == self.shaclNS.minLength:
    if constraints_current.get(self.shaclNS.minLength, None) != None:
        pass
    else:
        if constraints_current.get(self.shaclNS.maxLength, None) == None:
            self.SHACL.add((identifier_path_current, constraint_add, constraint_add_value))
        elif constraint_add_value <= constraints_current.get(self.shaclNS.maxLength):
            self.SHACL.add((identifier_path_current, constraint_add, constraint_add_value))

elif constraint_add == self.shaclNS.maxLength:
    if constraints_current.get(self.shaclNS.maxLength, None) != None:
        pass
    else:
        if constraints_current.get(self.shaclNS.minLength, None) == None:
            self.SHACL.add((identifier_path_current, constraint_add, constraint_add_value))
        elif constraint_add_value >= constraints_current.get(self.shaclNS.minLength):
            self.SHACL.add((identifier_path_current, constraint_add, constraint_add_value))

elif constraint_add == self.shaclNS.pattern:
    if constraints_current.get(self.shaclNS.pattern, None) != None:
        pass
    else:
        self.SHACL.add((identifier_path_current, constraint_add, constraint_add_value))

elif constraint_add == self.shaclNS.flags:
    if constraints_current.get(self.shaclNS.flags, None) != None:
        pass
    else:
        self.SHACL.add((identifier_path_current, constraint_add, constraint_add_value))

elif constraint_add == self.shaclNS.languageIn:
    _, languageIn_add = self.findList(shape_add, constraint_add_value, [])
    if languageIn_add == []:
        return None

    if constraints_current.get(self.shaclNS.languageIn, None) != None:
        for s, p, o in self.SHACL.triples((identifier_path_current, self.shaclNS.languageIn, None)):    
            node_current = o
            break
        _, languageIn_current = self.findList(self.SHACL, node_current, [])
    else:
        node_current = BNode()
        self.SHACL.add((identifier_path_current, constraint_add, node_current))
        languageIn_current = []
    languageIn_merge = list(set(languageIn_current+languageIn_add))

    self.transformList(node_current, languageIn_merge)

elif constraint_add == self.shaclNS.uniqueLang:
    if constraints_current.get(self.shaclNS.uniqueLang, None) != None:
        pass
    else:
        self.SHACL.add((identifier_path_current, constraint_add, constraint_add_value))

elif constraint_add == self.shaclNS.equals:
    self.SHACL.add((identifier_path_current, constraint_add, constraint_add_value))

elif constraint_add == self.shaclNS.disjoint:
    self.SHACL.add((identifier_path_current, constraint_add, constraint_add_value))

elif constraint_add == self.shaclNS.lessThan:
    self.SHACL.add((identifier_path_current, constraint_add, constraint_add_value))

elif constraint_add == self.shaclNS.lessThanOrEquals:
    self.SHACL.add((identifier_path_current, constraint_add, constraint_add_value))

elif constraint_add == self.shaclNS["not"]:
    self.SHACL.add((identifier_path_current, constraint_add, constraint_add_value))
    self.SHACL += self.extractSubgraph(shape_add, constraint_add_value)

elif constraint_add == self.shaclNS["and"]:
    self.SHACL.add((identifier_path_current, constraint_add, constraint_add_value))
    self.SHACL += self.extractSubgraph(shape_add, constraint_add_value)

elif constraint_add == self.shaclNS["or"]:
    self.SHACL.add((identifier_path_current, constraint_add, constraint_add_value))
    self.SHACL += self.extractSubgraph(shape_add, constraint_add_value)

elif constraint_add == self.shaclNS.xone:
    self.SHACL.add((identifier_path_current, constraint_add, constraint_add_value))
    self.SHACL += self.extractSubgraph(shape_add, constraint_add_value)

elif constraint_add == self.shaclNS["node"]:
    self.SHACL.add((identifier_path_current, constraint_add, constraint_add_value))
    self.SHACL += self.extractSubgraph(shape_add, constraint_add_value)

elif constraint_add == self.shaclNS.hasValue:
    self.SHACL.add((identifier_path_current, constraint_add, constraint_add_value))

elif constraint_add == self.shaclNS["in"]:
    _, In_add = self.findList(shape_add, constraint_add_value, [])
    if In_add == []:
        return None

    if constraints_current.get(self.shaclNS["in"], None) != None:
        for s, p, o in self.SHACL.triples((identifier_path_current, self.shaclNS["in"], None)):
            node_current = o
            break
        _, In_current = self.findList(self.SHACL, node_current, [])
    else:
        node_current = BNode()
        self.SHACL.add((identifier_path_current, constraint_add, node_current))
        In_current = []
    In_merge = list(set(In_current+In_add))

    self.transformList(node_current, In_merge)
else:
    self.SHACL.add((identifier_path_current, constraint_add, constraint_add_value))
