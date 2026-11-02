# Extracted from JonAnderAsua/TFG-KG-RelacionesClientelares@82875c5f94 : procesSource/source/gate_cloud.py
# region: TextToTriple.grafoaSortu (lines 101-113, stratum add_run_shared_subject)
# licence of the source repository: see meta.json
from rdflib import URIRef, RDFS, Literal
from rdflib.namespace import RDF
from context_shim import TextToTripleStub

def grafoaSortu(self,json):
    for i in json:
        try:
            annotation_type = i['annotationType']['value']
            annotation_text = i['annotationText']['value']
            if annotation_type not in ('Sentence', 'Money', 'Date'):
                balioztatu, obj = self.balioztatu(annotation_text, annotation_type)
                if balioztatu:
                    subjektua = URIRef(self.bilatuUria(annotation_text))
                    self.grafoa += [(subjektua, RDF.type, URIRef(self.getType(obj))),
                                    (subjektua, RDFS.label, Literal(annotation_text))]
        except:
            pass


# Demo harness (identical on both sides, see meta.json): grafoaSortu takes
# `self` and mutates `self.grafoa` rather than returning anything, and a
# TextToTripleStub has no `__eq__`, so comparing it as a call argument would
# compare object identity and always fail. This wraps the call in a fresh
# stub per invocation and hands back the graph it wrote to, compared by
# isomorphism as usual.
def demo(annotations, validations, uris):
    self = TextToTripleStub(validations, uris)
    grafoaSortu(self, annotations)
    return self.grafoa
