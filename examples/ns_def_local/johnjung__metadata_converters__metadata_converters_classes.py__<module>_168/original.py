# Extracted from johnjung/metadata_converters@36a81d6a97 : metadata_converters/classes.py
# region: <module> (lines 168-225, stratum ns_def_local)
# licence of the source repository: see meta.json
import datetime, getpass, hashlib, jinja2, json, magic, os, \
       pymarc, random, re, string, sys
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF, DC, DCTERMS, XSD
BF = Namespace('http://id.loc.gov/ontologies/bibframe/')
EDM = Namespace('http://www.europeana.eu/schemas/edm/')
ERC = Namespace('https://www.dublincore.org/groups/kernel/spec/')
MADSRDF = Namespace('http://www.loc.gov/mads/rdf/v1#')
MIX = Namespace('http://www.loc.gov/mix/v20/')
ORE = Namespace('http://www.openarchives.org/ore/terms/')
PREMIS = Namespace('info:lc/xmlns/premis-v2/')
PREMIS2 = Namespace('http://www.loc.gov/premis/rdf/v1#')
PREMIS3 = Namespace('http://www.loc.gov/premis/rdf/v3/')

class DigitalCollectionToEDM:
    MAPS = Namespace('https://repository.lib.uchicago.edu/digital_collections/maps')
    MAPS_AGG = MAPS['/aggregation']
    MAPS_CHO = MAPS['']
    MAPS_REM = MAPS['/rem']

    CHISOC = Namespace('https://repository.lib.uchicago.edu/digital_collections/maps/chisoc')
    CHISOC_AGG = CHISOC['/aggregation']
    CHISOC_CHO = CHISOC['']
    CHISOC_REM = CHISOC['/rem']

    graph = Graph()
    for prefix, ns in (('bf', BF), ('dc', DC), ('dcterms', DCTERMS),
                       ('edm', EDM), ('erc', ERC), ('madsrdf', MADSRDF),
                       ('mix', MIX), ('ore', ORE), ('premis', PREMIS),
                       ('premis2', PREMIS2), ('premis3', PREMIS3)):
        graph.bind(prefix, ns)

    def __init__(self):
        self.graph = Graph()
        for prefix, ns in (('bf', BF), ('dc', DC), ('dcterms', DCTERMS),
                           ('edm', EDM), ('erc', ERC), ('madsrdf', MADSRDF),
                           ('mix', MIX), ('ore', ORE), ('premis', PREMIS),
                           ('premis2', PREMIS2), ('premis3', PREMIS3)):
            self.graph.bind(prefix, ns)

        self.now = Literal(datetime.datetime.utcnow(), datatype=XSD.dateTime)

    def agg_graph(self, agg, cho, rem, wbr):
        for p, o in ((RDF.type,          ORE.Aggregation),
                     (EDM.aggregatedCHO, cho),
                     (EDM.dataProvider,  Literal("University of Chicago Library")),
                     (ORE.isDescribedBy, rem),
                     (EDM.isShownAt,     wbr),
                     (EDM.isShownBy,     wbr),
                     (EDM.object,        URIRef('http://example.org/')),
                     (EDM.provider,      Literal('University of Chicago Library')),
                     (EDM.rights,        URIRef('http://creativecommons.org/licenses/by-nc/4.0/'))):
            self.graph.add((agg, p, o))

    def rem_graph(self, agg, rem, now):
        # as per CB on 11/6/2020, DCTERMS:creator should be
        # https://repository.lib.uchicago.edu/ - note https and trailing
        # slash, while ProvidedCHOs should not include a trailing slash.
        for p, o in ((RDF.type,         ORE.ResourceMap),
                     (DCTERMS.modified, now),
                     (DCTERMS.creator,  URIRef('https://repository.lib.uchicago.edu/')),
                     (ORE.describes,    agg)):
            self.graph.add((rem, p, o))

    @classmethod
    def triples(self):
        """Return EDM data as a string.

        Returns:
            str
        """
        return self.graph.serialize(format='turtle', base='ark:/61001/').decode("utf-8")
