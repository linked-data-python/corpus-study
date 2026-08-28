# Extracted from dtai-kg/SCOOP@40c6fc0420 : SCOOP/shape_generator/xsd2shacl/src/XSDtoSHACL.py
# region: XSDtoSHACL.transUnion (lines 515-600, stratum add_isolated)
# licence of the source repository: see meta.json
from rdflib import Graph, Literal, BNode, Namespace, RDF, URIRef

elif xsd_element.get("memberTypes") and len(xsd_element)>0 :
    memberTypes = xsd_element.get("memberTypes").split(" ")

    current_BN = BNode()
    self.SHACL.add((subject, self.shaclNS["or"], current_BN))

    for index in range(len(memberTypes)):
        memberType = memberTypes[index]
        if (":" in memberType) and (memberType.split(":")[-1] in self.type_list):
            shape_BN = BNode()
            self.SHACL.add((current_BN, RDF.first, shape_BN)) 
            self.SHACL.add((shape_BN, self.shaclNS.datatype, self.xsdNS[memberType.split(":")[1]])) 
            next_BN = BNode()
            if index == len(memberTypes)-1:
                self.SHACL.add((current_BN, RDF.rest, RDF.nil)) 
            else:   
                self.SHACL.add((current_BN, RDF.rest, next_BN))
            current_BN = next_BN
        else:
            sub_node = self.root.find(f'.//*[@name="{memberType}"]',self.xsdNSdict)
            element_type = self.isSimpleComplex(sub_node, memberType)
            if element_type == 1:
                self.SHACL.add((current_BN, RDF.first, self.NS[f'NodeShape/{memberType}'])) 
                next_BN = BNode()  
                self.SHACL.add((current_BN, RDF.rest, next_BN))
                current_BN = next_BN
            elif element_type == 0:
                sub_BN = BNode()
                self.SHACL.add((current_BN, RDF.first, sub_BN))
                self.shapes.append(sub_BN)
                self.translate(sub_node)
                self.shapes.pop()
                next_BN = BNode()
                self.SHACL.add((current_BN, RDF.rest, next_BN))
                current_BN = next_BN         
    index = 0
    for sub_node in xsd_element:
        index += 1
        element_type = self.isSimpleComplex(sub_node)
        if element_type == 1:
            self.SHACL.add((current_BN, RDF.first, self.NS[f'NodeShape/{memberType}'])) 
            next_BN = BNode()
            if index == len(memberTypes)-1:
                self.SHACL.add((current_BN, RDF.rest, RDF.nil)) 
            else:   
                self.SHACL.add((current_BN, RDF.rest, next_BN))
            current_BN = next_BN
        elif element_type == 0:
            sub_BN = BNode()
            self.SHACL.add((current_BN, RDF.first, sub_BN))
            self.shapes.append(sub_BN)
            self.translate(sub_node)
            self.shapes.pop()
            next_BN = BNode()
            if index == len(xsd_element):
                self.SHACL.add((current_BN, RDF.rest, RDF.nil)) 
            else:   
                self.SHACL.add((current_BN, RDF.rest, next_BN))
            current_BN = next_BN         
else:
    current_BN = BNode()
    self.SHACL.add((subject, self.shaclNS["or"], current_BN))
    index = 0
    for sub_node in xsd_element:
        index += 1
        element_type = self.isSimpleComplex(sub_node)
        if element_type == 1:
            self.SHACL.add((current_BN, RDF.first, self.NS[f'NodeShape/{memberType}'])) 
            next_BN = BNode()
            if index == len(memberTypes)-1:
                self.SHACL.add((current_BN, RDF.rest, RDF.nil)) 
            else:   
                self.SHACL.add((current_BN, RDF.rest, next_BN))
            current_BN = next_BN
        elif element_type == 0:
            sub_BN = BNode()
            self.SHACL.add((current_BN, RDF.first, sub_BN))
            self.shapes.append(sub_BN)
            self.translate(sub_node)
            self.shapes.pop()
            next_BN = BNode()
            if index == len(xsd_element):
                self.SHACL.add((current_BN, RDF.rest, RDF.nil)) 
            else:   
                self.SHACL.add((current_BN, RDF.rest, next_BN))
            current_BN = next_BN         
