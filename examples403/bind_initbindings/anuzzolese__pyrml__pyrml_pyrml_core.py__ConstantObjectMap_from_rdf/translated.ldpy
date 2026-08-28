# Extracted from anuzzolese/pyrml@d18fe2edfc : pyrml/pyrml_core.py
# region: ConstantObjectMap.from_rdf (lines 72-114, stratum bind_initbindings)
# licence of the source repository: see meta.json
from pyrml import rml_vocab
from typing import Dict, Union, Set, List, Type, Generator
from pyrml.pyrml_api import PyRML, DataSource, TermMap, AbstractMap, TermUtils, graph_add_all, Expression, FunctionNotRegisteredException, NoneFunctionException, ParameterNotExintingInFunctionException, RMLModelException
from rdflib import URIRef, Graph, IdentifiedNode
from rdflib.plugins.sparql.processor import prepareQuery
from rdflib.term import Node, BNode, Literal, Identifier, URIRef, _is_valid_langtag, _castPythonToLiteral, _castLexicalToPython 
import pyrml.rml_vocab as rml_vocab

@staticmethod
def from_rdf(g: Graph, parent: Union[BNode, URIRef] = None) -> Set[TermMap]:
    term_maps = set()
    mappings_dict = PyRML.get_mapper().get_mapping_dict()

    query = prepareQuery(
        """
            SELECT DISTINCT ?p ?c
            WHERE {
                {
                    ?p rr:constant ?c1
                    BIND(?c1 AS ?c)
                }
                UNION
                {
                    OPTIONAL{?p rr:constant ?c2}
                    FILTER(!BOUND(?c2))
                    FILTER(isIRI(?p))
                    BIND(?p AS ?c)
                }
        }""", 
        initNs = { "rr": rml_vocab.RR})

    if parent is not None:
        qres = g.query(query, initBindings = { "p": parent})
    else:
        qres = g.query(query)

    for row in qres:

        c = None
        if isinstance(row.p, URIRef):
            if row.p in mappings_dict:
                c = mappings_dict.get(row.p)
            else:
                c = ConstantObjectMap(row.c, row.p)
                mappings_dict.add(c)
        else:
            c = ConstantObjectMap(row.c)

        term_maps.add(c)

    return term_maps
