# Context shim (see meta.json): subset of
# johnjung/metadata_converters@36a81d6a97 : metadata_converters/classes.py,
# so the region executes outside the package (`from classes import ...`
# needs a sibling classes.py this extraction does not carry).
#
# BASE is a genuine upstream inconsistency, not something introduced here:
# `git show 36a81d6a97:metadata_converters/classes.py` defines ARK, BF, EDM,
# ERC, MADSRDF, MIX, OAI, ORE, PREMIS, PREMIS2, PREMIS3, VRA -- but no BASE.
# `from classes import BASE, ...` (mepa_edm.py's own context line, kept
# verbatim in original.py) would raise ImportError at this commit if run
# against the real classes.py. BASE is not referenced anywhere inside THIS
# region's own body, so the value below is only a harmless placeholder that
# lets the import line resolve; picked to match the base already used a few
# lines below in the real file, DigitalCollectionToEDM.triples():
# `self.graph.serialize(format='turtle', base='ark:/61001/')`.
#
# DigitalCollectionToEDM.__init__/agg_graph/rem_graph are copied verbatim
# from classes.py lines 186-213 (MAPS/CHISOC and .triples() are not reached
# by this region or its demo stub and are left out, not simplified) --
# needed because build_mepa_collection_triples calls self.agg_graph/
# self.rem_graph as plumbing outside the translated lines (see original.py's
# demo harness).
import datetime

from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF, DC, DCTERMS, XSD

BASE = 'ark:/61001/'
ARK = Namespace('ark:/61001/')
BF = Namespace('http://id.loc.gov/ontologies/bibframe/')
EDM = Namespace('http://www.europeana.eu/schemas/edm/')
ERC = Namespace('https://www.dublincore.org/groups/kernel/spec/')
MADSRDF = Namespace('http://www.loc.gov/mads/rdf/v1#')
MIX = Namespace('http://www.loc.gov/mix/v20/')
OAI = Namespace('http://www.openarchives.org/OAI/2.0/')
ORE = Namespace('http://www.openarchives.org/ore/terms/')
PREMIS = Namespace('info:lc/xmlns/premis-v2/')
PREMIS2 = Namespace('http://www.loc.gov/premis/rdf/v1#')
PREMIS3 = Namespace('http://www.loc.gov/premis/rdf/v3/')
VRA = Namespace('http://purl.org/vra/')

__namespaces__ = {
    "bf": BF, "edm": EDM, "erc": ERC, "madsrdf": MADSRDF, "mix": MIX,
    "oai": OAI, "ore": ORE, "premis": PREMIS, "premis2": PREMIS2,
    "premis3": PREMIS3, "vra": VRA,
}


class DigitalCollectionToEDM:
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
        for p, o in ((RDF.type,         ORE.ResourceMap),
                     (DCTERMS.modified, now),
                     (DCTERMS.creator,  URIRef('https://repository.lib.uchicago.edu/')),
                     (ORE.describes,    agg)):
            self.graph.add((rem, p, o))
