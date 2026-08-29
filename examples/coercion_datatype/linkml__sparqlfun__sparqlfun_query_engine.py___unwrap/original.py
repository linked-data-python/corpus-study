# Extracted from linkml/sparqlfun@0894c75fcf : sparqlfun/query_engine.py
# region: _unwrap (lines 419-432, stratum coercion_datatype)
# licence of the source repository: see meta.json
import SPARQLWrapper.SmartWrapper as sw
from rdflib import URIRef, Graph, Literal, BNode, RDF
from rdflib.term import Node, Identifier

def _unwrap(v: sw.Value) -> Node:
    if v.type == sw.Value.URI:
        return URIRef(v.value)
    elif v.type == sw.Value.Literal:
        if v.lang is not None:
            return Literal(v.value, lang=v.lang)
        else:
            return Literal(v.value)
    elif v.type == sw.Value.TypedLiteral:
        return Literal(v.value, datatype=v.datatype)
    elif v.type == sw.Value.BNODE:
        return BNode(v.value)
    else:
        raise Exception(f'Unknown type {v.type} for {v}')
