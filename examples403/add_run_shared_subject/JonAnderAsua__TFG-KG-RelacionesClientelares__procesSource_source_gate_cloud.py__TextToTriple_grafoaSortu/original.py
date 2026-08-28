# Extracted from JonAnderAsua/TFG-KG-RelacionesClientelares@82875c5f94 : procesSource/source/gate_cloud.py
# region: TextToTriple.grafoaSortu (lines 101-113, stratum add_run_shared_subject)
# licence of the source repository: see meta.json
from SPARQLWrapper import SPARQLWrapper, BASIC, INSERT, POST, SELECT, GET, JSON,RDF
from rdflib import Graph,URIRef, RDFS, Literal
from rdflib.namespace import RDF

def grafoaSortu(self,json):
    for i in json:
        try:
            if(i['annotationType']['value'] != 'Sentence' and i['annotationType']['value'] != 'Money' and i['annotationType']['value'] != 'Date'):
                balioztatu, obj = self.balioztatu(i['annotationText']['value'],i['annotationType']['value'])
                if(balioztatu):
                    uria = self.bilatuUria(i['annotationText']['value'])
                    subjektua = URIRef(uria)
                    objektua = URIRef(self.getType(obj))
                    self.grafoa.add((subjektua,RDF.type,objektua))
                    self.grafoa.add((subjektua,RDFS.label,Literal(i['annotationText']['value'])))
        except:
            pass
