# Extracted from MKLab-ITI/prophet@eee2ab51de : rdflib/extras/infixowl.py
# region: AnnotatableTerms.setupACEAnnotations (lines 529-560, band medium)
# licence of the source repository: see meta.json
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
