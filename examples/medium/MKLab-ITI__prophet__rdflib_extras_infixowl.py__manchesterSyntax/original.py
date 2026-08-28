# Extracted from MKLab-ITI/prophet@eee2ab51de : rdflib/extras/infixowl.py
# region: manchesterSyntax (lines 254-356, band medium)
# licence of the source repository: see meta.json
import logging
from rdflib import (
    BNode,
    Literal,
    Namespace,
    RDF,
    RDFS,
    URIRef,
    Variable
)
from rdflib.collection import Collection
from rdflib.util import first
# context shim (see meta.json): Class is defined further down in the enclosing
# infixowl.py, vendored as infixowl_context.py
from infixowl_context import Class
logger = logging.getLogger(__name__)
OWL_NS = Namespace("http://www.w3.org/2002/07/owl#")
nsBinds = {
    'skos': 'http://www.w3.org/2004/02/skos/core#',
    'rdf': RDF,
    'rdfs': RDFS,
    'owl': OWL_NS,
    'list': URIRef('http://www.w3.org/2000/10/swap/list#'),
    'dc': "http://purl.org/dc/elements/1.1/",
}

def manchesterSyntax(thing, store, boolean=None, transientList=False):
    """
    Core serialization
    """
    assert thing is not None
    if boolean:
        if transientList:
            liveChildren = iter(thing)
            children = [manchesterSyntax(child, store) for child in thing]
        else:
            liveChildren = iter(Collection(store, thing))
            children = [manchesterSyntax(
                child, store) for child in Collection(store, thing)]
        if boolean == OWL_NS.intersectionOf:
            childList = []
            named = []
            for child in liveChildren:
                if isinstance(child, URIRef):
                    named.append(child)
                else:
                    childList.append(child)
            if named:
                def castToQName(x):
                    prefix, uri, localName = store.compute_qname(x)
                    return ':'.join([prefix, localName])

                if len(named) > 1:
                    prefix = u'( ' + u' AND '.join(map(
                        castToQName, named)) + u' )'
                else:
                    prefix = manchesterSyntax(named[0], store)
                if childList:
                    return str(prefix) + u' THAT ' + u' AND '.join(
                        [str(manchesterSyntax(x, store)) for x in childList])
                else:
                    return prefix
            else:
                return u'( ' + u' AND '.join(
                    [str(c) for c in children]) + u' )'
        elif boolean == OWL_NS.unionOf:
            return u'( ' + u' OR '.join([str(c) for c in children]) + ' )'
        elif boolean == OWL_NS.oneOf:
            return u'{ ' + u' '.join([str(c) for c in children]) + ' }'
        else:
            assert boolean == OWL_NS.complementOf
    elif OWL_NS.Restriction in store.objects(
            subject=thing, predicate=RDF.type):
        prop = list(
            store.objects(subject=thing, predicate=OWL_NS.onProperty))[0]
        prefix, uri, localName = store.compute_qname(prop)
        propString = u':'.join([prefix, localName])
        label = first(store.objects(subject=prop, predicate=RDFS.label))
        if label:
            propString = "'%s'" % label
        for onlyClass in store.objects(
                subject=thing, predicate=OWL_NS.allValuesFrom):
            return u'( %s ONLY %s )' % (
                propString, manchesterSyntax(onlyClass, store))
        for val in store.objects(subject=thing, predicate=OWL_NS.hasValue):
            return u'( %s VALUE %s )' % (
                propString,
                manchesterSyntax(val.encode('utf-8', 'ignore'), store))
        for someClass in store.objects(
                subject=thing, predicate=OWL_NS.someValuesFrom):
            return u'( %s SOME %s )' % (
                propString, manchesterSyntax(someClass, store))
        cardLookup = {OWL_NS.maxCardinality: 'MAX',
                      OWL_NS.minCardinality: 'MIN',
                      OWL_NS.cardinality: 'EQUALS'}
        for s, p, o in store.triples_choices(
                (thing, list(cardLookup.keys()), None)):
            return u'( %s %s %s )' % (
                propString, cardLookup[p], o.encode('utf-8', 'ignore'))
    compl = list(store.objects(subject=thing, predicate=OWL_NS.complementOf))
    if compl:
        return '( NOT %s )' % (manchesterSyntax(compl[0], store))
    else:
        prolog = '\n'.join(
            ["PREFIX %s: <%s>" % (k, nsBinds[k]) for k in nsBinds])
        qstr = \
            prolog + \
            "\nSELECT ?p ?bool WHERE {?class a owl:Class; ?p ?bool ." + \
            "?bool rdf:first ?foo }"
        initb = {Variable("?class"): thing}
        for boolProp, col in \
                store.query(qstr, processor="sparql", initBindings=initb):
            if not isinstance(thing, URIRef):
                return manchesterSyntax(col, store, boolean=boolProp)
        try:
            prefix, uri, localName = store.compute_qname(thing)
            qname = u':'.join([prefix, localName])
        except Exception:
            if isinstance(thing, BNode):
                return thing.n3()
            return u"<" + thing + ">"
            logger.debug(list(store.objects(subject=thing, predicate=RDF.type)))
            raise
            return '[]'  # +thing._id.encode('utf-8')+'</em>'
        label = first(Class(thing, graph=store).label)
        if label:
            return label.encode('utf-8', 'ignore')
        else:
            return qname.encode('utf-8', 'ignore')
