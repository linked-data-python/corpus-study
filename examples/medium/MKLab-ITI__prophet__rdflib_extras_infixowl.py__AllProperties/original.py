# Extracted from MKLab-ITI/prophet@eee2ab51de : rdflib/extras/infixowl.py
# region: AllProperties (lines 668-689, band medium)
# licence of the source repository: see meta.json
from rdflib import (
    BNode,
    Literal,
    Namespace,
    RDF,
    RDFS,
    URIRef,
    Variable
)
from rdflib.extras.infixowl import Property   # context shim, see meta.json
OWL_NS = Namespace("http://www.w3.org/2002/07/owl#")

def AllProperties(graph):
    prevProps = set()
    for s, p, o in graph.triples_choices(
        (None, RDF.type, [OWL_NS.SymmetricProperty,
                          OWL_NS.FunctionalProperty,
                          OWL_NS.InverseFunctionalProperty,
                          OWL_NS.TransitiveProperty,
                          OWL_NS.DatatypeProperty,
                          OWL_NS.ObjectProperty,
                          OWL_NS.AnnotationProperty])):
        if o in [OWL_NS.SymmetricProperty,
                 OWL_NS.InverseFunctionalProperty,
                 OWL_NS.TransitiveProperty,
                 OWL_NS.ObjectProperty]:
            bType = OWL_NS.ObjectProperty
        else:
            bType = OWL_NS.DatatypeProperty
        if s not in prevProps:
            prevProps.add(s)
            yield Property(s,
                           graph=graph,
                           baseType=bType)


# --- demo harness (added identically to both representations; see meta.json) ---
# AllProperties is a generator yielding infixowl Property objects, which the
# driver cannot compare directly; the harness consumes it, prints the
# properties it recognised and their base type, and leaves the graph -- which
# Property.__init__ mutates by asserting the base type -- at module level so
# the driver can compare it by isomorphism.
from rdflib import Graph

demo_graph = Graph()
demo_graph.parse(data="""
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix ex:  <http://example.org/> .
ex:knows      a owl:ObjectProperty, owl:SymmetricProperty .
ex:ancestorOf a owl:TransitiveProperty .
ex:age        a owl:DatatypeProperty, owl:FunctionalProperty .
ex:note       a owl:AnnotationProperty .
ex:ssn        a owl:InverseFunctionalProperty .
ex:notAProp   a owl:Class .
""", format="turtle")

for _prop in list(AllProperties(demo_graph)):
    print(_prop.identifier, "->", _prop._baseType)
