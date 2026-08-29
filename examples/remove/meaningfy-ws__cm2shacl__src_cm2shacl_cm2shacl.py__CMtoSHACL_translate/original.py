# Extracted from meaningfy-ws/cm2shacl@ec908f3d43 : src/cm2shacl/cm2shacl.py
# region: CMtoSHACL.translate (lines 31-117, stratum remove)
# licence of the source repository: see meta.json
from rdflib import Graph, URIRef, Literal, Namespace, BNode
from rdflib.namespace import RDF, RDFS,XSD, SH
from .utils import json_load, combine_shapes_with_same_path

def translate(self):
    # load the data
    self.metaData_info, self.Class_path, self.Property_path, self.Field_XPath, self.controlled_list_c1, self.controlled_list_c2, self.field_id = self.dL.load()
    self.controlled_list_c1 = self.controlled_list_c1["CL1"]
    self.controlled_list_c2 = self.controlled_list_c2["CL2"]

    # loop through the rules
    multi_list = []
    for XPath, Class, Property, ID in zip(self.Field_XPath, self.Class_path, self.Property_path, self.field_id):
        # print(f"Processing Rule {num}...")
        # print(f"C: {Class}, P: {Property}")
        # if 'FILTER' in Property or num == 551: #TODO: to be fixed Lot and FILTER
        if 'FILTER' in Property: #TODO: to be fixed Lot and FILTER
            continue
        if ("OR" in Class) and ("{" in Property) and ("UNION" in Property):
            Class = [i for i in Class.split("OR")]
            Property = [i.replace("{","").replace("}","").strip() for i in Property.split("UNION")] 
            # Cartesian Product
            for i in range(len(Class)):
                c_list = self.parseClassPath(Class[i], XPath)
                p_list = self.parsePropertyPath(Property[i])
                multi_list.append((c_list, p_list))
        elif ("OR" in Class) and ("{" not in Property) and ("UNION" not in Property):
            Class = [i for i in Class.split("OR")]
            p_list = self.parsePropertyPath(Property)
            for c in Class:
                c_list = self.parseClassPath(c, XPath)
                multi_list.append((c_list, p_list))
        elif ("OR" not in Class) and ("{" in Property) and ("UNION" in Property):
            Property = [i.replace("{","").replace("}","").strip() for i in Property.split("UNION")]
            c_list = self.parseClassPath(Class, XPath)
            for p in Property:
                p_list = self.parsePropertyPath(p)
                multi_list.append((c_list, p_list))
        else:
            c_list = self.parseClassPath(Class, XPath)
            p_list = self.parsePropertyPath(Property)

        if multi_list == []:
            if len(c_list) != len(p_list) and len(p_list)>=2 and p_list[-2] == RDF.type:
                p_list = p_list[:-2]
                p_list.append("?value")
            if len(c_list) != len(p_list):
                if len(p_list) == 2 and p_list[0] == RDF.type:
                    print("The length of the rule is not consistent: ", ID)
                else:
                    print("The length of the rule is not consistent: ", ID)
                    print("class list: ", c_list)
                    print("property list: ", p_list)
            else:
                for index in range(len(c_list) - 1):
                    c = c_list[index]
                    p = p_list[index]
                    if index == len(c_list)-2:
                        self.addNodePropertyShape(c, p, c_list[index+1], p_list[index+1], ID, True)
                    else:
                        self.addNodePropertyShape(c, p, c_list[index+1], p_list[index+1], ID)
        else:
            for c_list, p_list in multi_list:
                if len(c_list) != len(p_list) and p_list[-2] == RDF.type:
                    p_list = p_list[:-2]
                    p_list.append("?value")
                if len(c_list) != len(p_list):
                    if len(p_list) == 2 and p_list[0] == RDF.type:
                        pass
                    else:
                        print("2The length of the rule is not consistent: ", ID)
                        print("class list: ", c_list)
                        print("property list: ", p_list)
                else:
                    for index in range(len(c_list) - 1):
                        c = c_list[index]
                        p = p_list[index]
                        if index == len(c_list)-2:
                            self.addNodePropertyShape(c, p, c_list[index+1], p_list[index+1], ID, True)
                        else:
                            self.addNodePropertyShape(c, p, c_list[index+1], p_list[index+1], ID)
            multi_list = []

    #self.addSHACLin()
    # self.addSHACLconstraints()
    # self.addDisjunctionShapes()
    self.g = combine_shapes_with_same_path(self.g)
    self.g.remove((None, SH["datatype"], RDF.langString))
    self.g.remove((None, SH["datatype"], XSD.anyURI))      
    self.g.remove((None, SH["datatype"], URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#plainLiteral"))) 
    self.g.remove((None, SH["datatype"], RDF.PlainLiteral))         
