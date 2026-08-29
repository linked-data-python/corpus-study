# Extracted from ReproNim/ants_seg_to_nidm@97e6257b08 : ants_seg_to_nidm/ants_seg_to_nidm.py
# region: add_seg_data (lines 105-105, stratum ns_def_local)
# licence of the source repository: see meta.json
from nidm.core import Constants
from rdflib import Graph, RDF, URIRef, util, term,Namespace,Literal,BNode,XSD

sio = Namespace(Constants.SIO)
