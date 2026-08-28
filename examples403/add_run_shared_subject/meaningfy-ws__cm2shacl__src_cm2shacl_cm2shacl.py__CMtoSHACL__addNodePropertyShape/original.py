# Extracted from meaningfy-ws/cm2shacl@ec908f3d43 : src/cm2shacl/cm2shacl.py
# region: CMtoSHACL._addNodePropertyShape (lines 119-164, stratum add_run_shared_subject)
# licence of the source repository: see meta.json
from rdflib import Graph, URIRef, Literal, Namespace, BNode
from rdflib.namespace import RDF, RDFS,XSD, SH

def _addNodePropertyShape(self, c, p, next_c, next_p, ID, is_last=False):
    c = URIRef(c)
    p = URIRef(p)
    if c not in self.identifiers:
        self.identifiers[c] = {}
        self.g.add((c, RDF.type, SH.NodeShape))
        self.g.add((c, self.dctsource, Literal(ID)))
        if self.close:
            self.g.add((c, SH.closed, Literal("true", datatype=XSD.boolean)))
            bn = BNode()
            self.g.add((c, SH.ignoredProperties, bn))
            self.g.add((bn, RDF.first, RDF.type))
            self.g.add((bn, RDF.rest, RDF.nil))
        self.g.add((c, SH.targetClass, c))
        self.g.add((c, SH["class"],c))
        self.g.add((c, SH["nodeKind"], SH["IRI"]))
    if p not in self.identifiers[c]:
        self.identifiers[c][p] = BNode()
        self.g.add((c, SH.property, self.identifiers[c][p]))
        self.g.add((self.identifiers[c][p], SH.path, p))
        self.g.add((self.identifiers[c][p], self.dctsource, Literal(ID)))

    if is_last == False and next_c != None:
        self.g.add((self.identifiers[c][p], SH["class"], URIRef(next_c)))
        self.g.add((self.identifiers[c][p], SH["nodeKind"], SH["IRI"]))
    elif is_last == True:
        next_c_type = self.checkType(next_c)
        if next_c_type == "class":
            # self.g.add((self.identifiers[c][p], SH["class"], URIRef(next_c)))
            currentClass = self.constraintDict[SH["class"]].get(self.identifiers[c][p], [])
            currentClass.append(URIRef(next_c))
            self.constraintDict[SH["class"]][self.identifiers[c][p]] = currentClass
            self.g.add((self.identifiers[c][p], SH["nodeKind"], SH["IRI"]))
        elif next_c_type == "datatype":
            # self.g.add((self.identifiers[c][p], SH["datatype"], next_c))
            currentDatatype = self.constraintDict[SH["datatype"]].get(self.identifiers[c][p], [])
            currentDatatype.append(next_c)
            self.constraintDict[SH["datatype"]][self.identifiers[c][p]] = currentDatatype
            self.g.add((self.identifiers[c][p], SH["nodeKind"], SH["Literal"]))
        elif next_c_type == None:
            self.g.add((self.identifiers[c][p], SH["nodeKind"], SH["IRI"]))
        if next_p != "?value":
            # self.g.add((self.identifiers[c][p], SH["hasValue"], Literal(next_p)))
            currentIn = self.shaclinDict.get(self.identifiers[c][p], [])
            currentIn.append(Literal(next_p))
            self.shaclinDict[self.identifiers[c][p]] = currentIn
