# Extracted from ArangoDB-Community/ArangoRDF@48cfed903a : arango_rdf/main.py
# region: ArangoRDF.__adb_val_to_rdf_val (lines 2101-2173, stratum coercion_datatype)
# licence of the source repository: see meta.json
import json
from typing import Any, Callable, DefaultDict, Dict, List, Optional, Set, Tuple, Union
from rdflib import RDF, RDFS, XSD, BNode
from rdflib import Literal, URIRef
from .typings import (
    ADBDocs,
    ADBMetagraph,
    Json,
    PredicateScope,
    RDFListData,
    RDFListHeads,
    RDFTerm,
    RDFTermMeta,
    TypeMap,
)

def __adb_val_to_rdf_val(
    self, col: str, s: RDFTerm, p: URIRef, val: Any, sg: Optional[URIRef] = None
) -> None:
    """ArangoDB -> RDF: Insert an arbitrary ArangoDB Document Property
    value into the RDF Graph.

    If the ArangoDB document property **val** is of type list
    or dict, then a recursive process is introduced to unpack
    the ArangoDB document property into multiple RDF Statements.
    Otherwise, the ArangoDB Document Property is treated as
    a Literal in the context of RDF.

    :param col: The ArangoDB Collection name of **s**.
    :type col: str
    :param s: The RDF Subject of the to-be-inserted RDF Statement.
    :type s: URIRef | BNode
    :param p: The RDF Predicate of the to-be-inserted RDF Statement.
        This represents the ArangoDB Document Property key name.
    :type p: URIRef
    :param sub_key: The ArangoDB property key of the document
        that will be used to store the value.
    :type sub_key: str
    :param val: Some RDF value to insert.
    :type val: Any
    :param sg: The Sub Graph URI of the (s,p,val) statement, if any.
    :type sg: URIRef | None
    """

    if isinstance(val, list):
        if self.__list_conversion == "static":
            for v in val:
                self.__adb_val_to_rdf_val(col, s, p, v, sg)

        elif self.__list_conversion == "collection":
            node: RDFTerm = BNode()
            self.__add_to_rdf_graph(s, p, node, sg)

            rest: RDFTerm
            for i, v in enumerate(val):
                self.__adb_val_to_rdf_val(col, node, RDF.first, v)

                rest = RDF.nil if i == len(val) - 1 else BNode()
                self.__add_to_rdf_graph(node, RDF.rest, rest, sg)
                node = rest

        elif self.__list_conversion == "container":
            bnode = BNode()
            self.__add_to_rdf_graph(s, p, bnode, sg)

            for i, v in enumerate(val, 1):
                _n = URIRef(f"{RDF}_{i}")
                self.__adb_val_to_rdf_val(col, bnode, _n, v, sg)

        else:  # serialize
            val = json.dumps(val)
            self.__add_to_rdf_graph(s, p, Literal(val), sg)

    elif isinstance(val, dict):
        if self.__dict_conversion == "static":
            bnode = BNode()
            self.__add_to_rdf_graph(s, p, bnode, sg)

            for k, v in val.items():
                p = self.__uri_map.get(k, URIRef(f"{self.__graph_ns}/{k}"))
                self.__adb_val_to_rdf_val(col, bnode, p, v, sg)

        else:  # serialize
            val = json.dumps(val)
            self.__add_to_rdf_graph(s, p, Literal(val), sg)

    else:
        # TODO: Datatype? Lang? Not yet sure how to handle this...
        self.__add_to_rdf_graph(s, p, Literal(val), sg)
