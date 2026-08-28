# Extracted from MKLab-ITI/prophet@eee2ab51de : rdflib/extras/infixowl.py
# region: ComponentTerms (lines 721-769, band medium)
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
OWL_NS = Namespace("http://www.w3.org/2002/07/owl#")
CLASS_RELATIONS = set(
    OWL_NS.resourceProperties
).difference([OWL_NS.onProperty,
              OWL_NS.allValuesFrom,
              OWL_NS.hasValue,
              OWL_NS.someValuesFrom,
              OWL_NS.inverseOf,
              OWL_NS.imports,
              OWL_NS.versionInfo,
              OWL_NS.backwardCompatibleWith,
              OWL_NS.incompatibleWith,
              OWL_NS.unionOf,
              OWL_NS.intersectionOf,
              OWL_NS.oneOf])

def ComponentTerms(cls):
    """
    Takes a Class instance and returns a generator over the classes that
    are involved in its definition, ignoring unamed classes
    """
    if OWL_NS.Restriction in cls.type:
        try:
            cls = CastClass(cls, Individual.factoryGraph)
            for s, p, innerClsId in cls.factoryGraph.triples_choices(
                (cls.identifier,
                 [OWL_NS.allValuesFrom,
                  OWL_NS.someValuesFrom],
                 None)):
                innerCls = Class(innerClsId, skipOWLClassMembership=True)
                if isinstance(innerClsId, BNode):
                    for _c in ComponentTerms(innerCls):
                        yield _c
                else:
                    yield innerCls
        except:
            pass
    else:
        cls = CastClass(cls, Individual.factoryGraph)
        if isinstance(cls, BooleanClass):
            for _cls in cls:
                _cls = Class(_cls, skipOWLClassMembership=True)
                if isinstance(_cls.identifier, BNode):
                    for _c in ComponentTerms(_cls):
                        yield _c
                else:
                    yield _cls
        else:
            for innerCls in cls.subClassOf:
                if isinstance(innerCls.identifier, BNode):
                    for _c in ComponentTerms(innerCls):
                        yield _c
                else:
                    yield innerCls
            for s, p, o in cls.factoryGraph.triples_choices(
                (classOrIdentifier(cls),
                 CLASS_RELATIONS,
                 None)
            ):
                if isinstance(o, BNode):
                    for _c in ComponentTerms(
                            CastClass(o, Individual.factoryGraph)):
                        yield _c
                else:
                    yield innerCls
