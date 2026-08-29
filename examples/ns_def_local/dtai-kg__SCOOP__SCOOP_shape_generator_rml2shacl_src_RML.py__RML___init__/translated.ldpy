# Extracted from dtai-kg/SCOOP@40c6fc0420 : SCOOP/shape_generator/rml2shacl/src/RML.py
# region: RML.__init__ (lines 20-46, stratum ns_def_local)
# licence of the source repository: see meta.json
from typing import Dict, Optional, Type
import rdflib
from rdflib.term import BNode, Identifier, URIRef
from .rml_model import (
    GraphMap,
    LogicalSource,
    ObjectMap,
    PredicateMap,
    PredicateObjectMap,
    SubjectMap,
    TermMap,
    TriplesMap,
)

def __init__(self):
    self.graph = rdflib.Graph()
    self.rmlNS = rdflib.Namespace('http://semweb.mmlab.be/ns/rml#')
    self.r2rmlNS = rdflib.Namespace('http://www.w3.org/ns/r2rml#')
    self.TEMPLATE = self.r2rmlNS.template
    self.REFERENCE = self.rmlNS.reference
    self.TERMTYPE = self.r2rmlNS.termType
    self.POM = self.r2rmlNS.predicateObjectMap
    self.PREDICATE = self.r2rmlNS.predicate
    self.PRED_MAP = self.r2rmlNS.predicateMap
    self.TRIPLES_MAP_CLASS = self.r2rmlNS.TriplesMap
    self.SUBJECT_MAP = self.r2rmlNS.subjectMap
    self.CLASS = self.r2rmlNS['class']
    self.OJBECT_MAP = self.r2rmlNS.objectMap
    self.IRI_CLASS = self.r2rmlNS.IRI
    self.LANGUAGE = self.r2rmlNS.language
    self.CONSTANT = self.r2rmlNS.constant
    self.OBJECT = self.r2rmlNS.object
    self.DATATYPE = self.r2rmlNS.datatype
    self.LOGICAL_SOURCE = self.rmlNS.logicalSource
    self.LOGICAL_TABLE = self.r2rmlNS.logicalTable

    # contains triple maps models from rml_model module 
    # the keys are the triples maps' IRI values 
    self.tm_model_dict: Dict[Identifier, TriplesMap] = dict()
    self.graphs = []
    self.refgraphs = []
