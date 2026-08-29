# Extracted from dtai-kg/SCOOP@40c6fc0420 : SCOOP/shape_generator/xsd2shacl/src/XSDtoSHACL.py
# region: XSDtoSHACL.transEnumeration (lines 441-468, stratum add_isolated)
# licence of the source repository: see meta.json
from rdflib import Graph, Literal, BNode, Namespace, RDF, URIRef

def transEnumeration(self, xsd_element):
    values = []
    subject = self.shapes[-1]
    parent_element = self.find_parent(xsd_element, self.root)

    if parent_element not in self.enumerationShapes:
        self.enumerationShapes.append(parent_element)
    else:
        return xsd_element

    for e in parent_element.findall('.//xs:enumeration',namespaces={"xs": "http://www.w3.org/2001/XMLSchema"}):
        if e.get("value"):
            values.append(e.get("value"))

    if values == []:
        return xsd_element
    else:
        current_BN = BNode()
        self.SHACL.add((subject, self.shaclNS["in"], current_BN))
        for index in range(len(values))[0:-1]:
            self.SHACL.add((current_BN, RDF.first, Literal(values[index]))) 
            next_BN = BNode()
            self.SHACL.add((current_BN, RDF.rest, next_BN)) 
            current_BN = next_BN

        self.SHACL.add((current_BN, RDF.first, Literal(values[-1]))) 
        self.SHACL.add((current_BN, RDF.rest, RDF.nil)) 
        return xsd_element  
