# Extracted from anuzzolese/pyrml@d18fe2edfc : pyrml/pyrml_core.py
# region: PredicateBuilder.build (lines 644-651, stratum trav_one_step)
# licence of the source repository: see meta.json
from pyrml import rml_vocab
from typing import Dict, Union, Set, List, Type, Generator
from rdflib import URIRef, Graph, IdentifiedNode
import pyrml.rml_vocab as rml_vocab

@staticmethod
def build(g: Graph, pom: IdentifiedNode) -> List[Predicate]:


    predicates = [ConstantPredicate(pred, pred) for pred in g.objects(pom, rml_vocab.RR_NS.predicate, True)]
    predicates += [PredicateMap.from_rdf(pred, pom) for pred in g.objects(pom, rml_vocab.RR_NS.predicateMap, True)]

    return predicates
