# Extracted from MKLab-ITI/prophet@eee2ab51de : rdflib/extras/infixowl.py
# region: AnnotatableTerms.setupACEAnnotations (lines 529-560, band medium)
# licence of the source repository: see meta.json
from rdflib import Graph, Namespace
from infixowl_shim import Property
OWL_NS = Namespace("http://www.w3.org/2002/07/owl#")
ACE_NS = Namespace('http://attempto.ifi.uzh.ch/ace_lexicon#')

def setupACEAnnotations(self):
    self.graph.bind('ace', ACE_NS, override=False)

    # PN_sg singular form of a proper name ()
    self.PN_sgProp = Property(ACE_NS.PN_sg,
                              baseType=OWL_NS.AnnotationProperty,
                              graph=self.graph)

    # CN_sg singular form of a common noun
    self.CN_sgProp = Property(ACE_NS.CN_sg,
                              baseType=OWL_NS.AnnotationProperty,
                              graph=self.graph)

    # CN_pl plural form of a common noun
    self.CN_plProp = Property(ACE_NS.CN_pl,
                              baseType=OWL_NS.AnnotationProperty,
                              graph=self.graph)

    # singular form of a transitive verb
    self.TV_sgProp = Property(ACE_NS.TV_sg,
                              baseType=OWL_NS.AnnotationProperty,
                              graph=self.graph)

    # plural form of a transitive verb
    self.TV_plProp = Property(ACE_NS.TV_pl,
                              baseType=OWL_NS.AnnotationProperty,
                              graph=self.graph)

    # past participle form a transitive verb
    self.TV_vbgProp = Property(ACE_NS.TV_vbg,
                               baseType=OWL_NS.AnnotationProperty,
                               graph=self.graph)

# --- demo harness, added identically to both representations (see meta.json).
# The region is a method lifted out of AnnotatableTerms, so it can only be
# observed by attaching it back to an object that carries a graph.


class _Annotatable:
    setupACEAnnotations = setupACEAnnotations

    def __init__(self, graph):
        self.graph = graph


demo_graph = Graph()
_annotatable = _Annotatable(demo_graph)
_annotatable.setupACEAnnotations()
print(sorted(str(p.identifier) for p in (
    _annotatable.PN_sgProp, _annotatable.CN_sgProp, _annotatable.CN_plProp,
    _annotatable.TV_sgProp, _annotatable.TV_plProp, _annotatable.TV_vbgProp)))
print("ace bound to:", dict(demo_graph.namespaces()).get("ace"))
