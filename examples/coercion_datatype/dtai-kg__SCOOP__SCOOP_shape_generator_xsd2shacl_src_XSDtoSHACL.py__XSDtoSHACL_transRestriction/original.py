# Extracted from dtai-kg/SCOOP@40c6fc0420 : SCOOP/shape_generator/xsd2shacl/src/XSDtoSHACL.py
# region: XSDtoSHACL.transRestriction (lines 75-144, stratum coercion_datatype)
# licence of the source repository: see meta.json
import rdflib
from rdflib import Graph, Literal, BNode, Namespace, RDF, URIRef

def transRestriction(self,tag,value,subject=None):

    if subject == None:
        subject = self.shapes[-1]

    if "type" in tag or "restriction" in tag:
        if ((":" in value) and (value.split(":")[1] in self.type_list)):
            p = self.shaclNS.datatype
            o = self.xsdNS[value.split(":")[1]]
            self.SHACL.add((subject,p,o))
        elif value in self.type_list:
            p = self.shaclNS.datatype
            o = self.xsdNS[value]
            self.SHACL.add((subject,p,o))

    elif "default" in tag:
        p = self.shaclNS.defaultValue
        o = Literal(value)
        self.SHACL.add((subject,p,o))

    elif "fixed" in tag:
        p = self.shaclNS["in"]
        o = Literal(value)
        bn = BNode()
        self.SHACL.add((subject,p,bn))
        self.SHACL.add((bn,RDF.first,o))
        self.SHACL.add((bn,RDF.rest,RDF.nil))

    elif "pattern" in tag:
        p = self.shaclNS.pattern
        o = Literal(value)
        self.SHACL.add((subject,p,o))

    elif "maxExclusive" in tag:
        p = self.shaclNS.maxExclusive
        o = Literal(int(value))
        self.SHACL.add((subject,p,o))

    elif "minExclusive" in tag:
        p = self.shaclNS.minExclusive
        o = Literal(int(value))
        self.SHACL.add((subject,p,o))

    elif "maxInclusive" in tag:
        p = self.shaclNS.maxInclusive
        o = Literal(int(value))
        self.SHACL.add((subject,p,o))

    elif "minInclusive" in tag:
        p = self.shaclNS.minInclusive
        o = Literal(int(value))
        self.SHACL.add((subject,p,o))

    elif "length" in tag:        
        p = self.shaclNS.minLength
        o = Literal(int(value))
        self.SHACL.add((subject,p,o))
        p = self.shaclNS.maxLength
        o = rdflib.Literal(int(value))
        self.SHACL.add((subject,p,o))

    elif "minLength" in tag:        
        p = self.shaclNS.minLength
        o = Literal(int(value))
        self.SHACL.add((subject,p,o))

    elif "maxLength" in tag:        
        p = self.shaclNS.maxLength
        o = Literal(int(value))
        self.SHACL.add((subject,p,o))
