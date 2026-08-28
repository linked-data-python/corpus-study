# Extracted from johnjung/metadata_converters@36a81d6a97 : metadata_converters/mepa_edm.py
# region: MepaToEDM.build_mepa_collection_triples (lines 351-376, stratum ns_import_project)
# licence of the source repository: see meta.json
import datetime
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF, DC, DCTERMS, XSD
from classes import BASE, BF, EDM, ERC, MADSRDF, MIX, OAI, ORE, PREMIS, PREMIS2, PREMIS3, VRA

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
