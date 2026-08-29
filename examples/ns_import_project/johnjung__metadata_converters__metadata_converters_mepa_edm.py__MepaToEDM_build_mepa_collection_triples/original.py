# Extracted from johnjung/metadata_converters@36a81d6a97 : metadata_converters/mepa_edm.py
# region: MepaToEDM.build_mepa_collection_triples (lines 351-376, stratum ns_import_project)
# licence of the source repository: see meta.json
import datetime
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF, DC, DCTERMS, XSD
from classes_context import BASE, BF, EDM, ERC, MADSRDF, MIX, OAI, ORE, PREMIS, PREMIS2, PREMIS3, VRA

@classmethod
def build_mepa_collection_triples(self):
    """Add triples for MEPA, and to connect items with each other.

    Side Effect:
        Add triples to self.graph
    """

    now = Literal(datetime.datetime.utcnow(), datatype=XSD.dateTime)

    # aggregation
    self.agg_graph(self.MEPA_AGG, self.MEPA_CHO, self.MEPA_REM, MEPA_WBR)

    # cultural heritage object
    for p, o in ((RDF.type,  EDM.ProvidedCHO),
                 (DC.date,   Literal('2020')),
                 (DC.title,  Literal('The University of Chicago Library Digital Repository')),
                 (ERC.who,   Literal('University of Chicago Library')),
                 (ERC.what,  Literal('The University of Chicago Library Digital Repository')),
                 (ERC.when,  Literal('2020')),
                 (ERC.where, self.MEPA_CHO),
                 (EDM.year,  Literal('2020'))):
        self.graph.add((self.MEPA_CHO, p, o))

    # resource map
    self.rem_graph(self.MEPA_AGG, self.MEPA_REM, now)

# Demo harness (identical on both sides, see meta.json): the region is a
# classmethod whose `self` parameter receives the CLASS object, not an
# instance -- MEPA_AGG/MEPA_CHO/MEPA_REM are set as INSTANCE attributes in
# the real MepaToEDM.__init__ (verified against
# johnjung/metadata_converters@36a81d6a97 : metadata_converters/mepa_edm.py
# lines 34-38), and agg_graph/rem_graph are plain instance methods on
# DigitalCollectionToEDM (classes.py lines 196-213) -- calling this method
# through the ordinary classmethod protocol, on either the class or an
# instance, raises AttributeError/TypeError against the real upstream code.
# A second, independent bug in the same commit: MEPA_WBR is used bare
# (not self.MEPA_WBR) at the call to agg_graph, and is never assigned
# anywhere in mepa_edm.py -- a NameError. Both verified directly against the
# pinned commit, not assumed. Neither bug is introduced by this extraction
# or by translating it; restoring the bindings the extraction lost
# (AGENT_BATCH's "163 regions" case) means giving `self` a real instance and
# calling the classmethod's own wrapped function directly (`.__func__`),
# bypassing the broken descriptor protocol rather than silently "fixing"
# the decorator -- the decorator, part of the extracted region above, is
# untouched.
from classes_context import DigitalCollectionToEDM


class MepaStub(DigitalCollectionToEDM):
    def __init__(self):
        super().__init__()
        MEPA = Namespace('https://repository.lib.uchicago.edu/digital_collections/mepa/')
        self.MEPA_AGG = MEPA['aggregation']
        self.MEPA_CHO = MEPA['']
        self.MEPA_REM = MEPA['rem']


# never assigned upstream (see note above); placeholder value in the same
# style as work_wbr's own fallback a few lines later in the real file.
MEPA_WBR = URIRef('http://example.org/')


def demo():
    stub = MepaStub()
    build_mepa_collection_triples.__func__(stub)
    return stub.graph
