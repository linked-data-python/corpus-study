# Extracted from anuzzolese/pyrml@d18fe2edfc : pyrml/pyrml_core.py
# region: TripleMappings.from_rdf (lines 1630-1643, stratum trav_existence)
# licence of the source repository: see meta.json
#
# `pyrml` is not installed in this environment. Restored rml_vocab and
# TripleMappings from a minimal context shim (pyrml_context.py, see
# meta.json); TermMap is used here only as a return-type annotation. Trimmed
# the rest of the original file's top-of-file import block down to what this
# function body actually references -- Dict/Union/Set/Type/Generator and the
# nine pyrml.pyrml_api names other than TermMap, plus the plain `URIRef`
# import, were never used by these 14 lines.
from typing import List
from rdflib import Graph, IdentifiedNode
from pyrml_context import rml_vocab, TermMap, TripleMappings

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
