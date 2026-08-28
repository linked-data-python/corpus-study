# Extracted from anuzzolese/pyrml@d18fe2edfc : pyrml/pyrml_core.py
# region: TripleMappings.from_rdf (lines 1630-1643, stratum trav_existence)
# licence of the source repository: see meta.json
from pyrml import rml_vocab
from typing import Dict, Union, Set, List, Type, Generator
from pyrml.pyrml_api import PyRML, DataSource, TermMap, AbstractMap, TermUtils, graph_add_all, Expression, FunctionNotRegisteredException, NoneFunctionException, ParameterNotExintingInFunctionException, RMLModelException
from rdflib import URIRef, Graph, IdentifiedNode
import pyrml.rml_vocab as rml_vocab

@staticmethod
def from_rdf(g: Graph, parent: IdentifiedNode = None) -> List[TermMap]:

    tm = None
    if parent:
        tm = g.value(parent, rml_vocab.RR_NS.parentTriplesMap)

    tps = g.triples((tm, rml_vocab.RML_NS.logicalSource|rml_vocab.RR_NS.logicalTable, None))

    triple_mappings = []
    for tm,p,o in tps:
        if g.value(tm, rml_vocab.RR_NS.subjectMap):
            triple_mappings.append(TripleMappings.__build(g, tm))
    return triple_mappings
