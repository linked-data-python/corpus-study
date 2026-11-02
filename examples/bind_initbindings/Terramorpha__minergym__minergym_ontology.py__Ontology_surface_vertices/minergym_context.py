# Context shim (see meta.json): the module-level names of
# minergym/ontology.py in Terramorpha/minergym@1d2d586bb1 that the extracted
# region needs (`TypeAlias`, the `IDF` namespace) and the two helpers that
# build the rdflib representation of an epJSON object (`create_rdf_list`,
# `intern_object`, copied verbatim), so the region executes outside the
# package. Identical bindings for both representations.
from typing import TypeAlias

import rdflib
from rdflib.namespace import RDF
from rdflib.term import Node

IDF = rdflib.Namespace("https://energyplus.net/")


def create_rdf_list(graph: rdflib.Graph, items: list[Node]):
    last = RDF.nil
    for item in reversed(items):
        new_node = rdflib.BNode()
        graph.add((new_node, RDF.first, item))
        graph.add((new_node, RDF.rest, last))
        last = new_node
        graph.add((last, RDF.type, RDF.List))

    return last


def intern_object(graph: rdflib.Graph, obj) -> Node:
    if isinstance(obj, str):
        return rdflib.Literal(obj)
    elif isinstance(obj, float):
        return rdflib.Literal(obj)
    elif isinstance(obj, int):
        return rdflib.Literal(obj)
    elif isinstance(obj, list):
        things = [intern_object(graph, v) for v in obj]
        return create_rdf_list(graph, things)
    elif isinstance(obj, dict):
        node = rdflib.BNode()

        for k, v in obj.items():
            interned_v = intern_object(graph, v)
            graph.add((node, IDF[k], interned_v))

        return node
    else:
        raise Exception(f"huh? {obj}, {type(obj)}")


def graph_from_object(obj) -> rdflib.Graph:
    """Body of `Ontology.from_object` (same file), minus the class."""
    g = rdflib.Graph()
    for type_name, value in obj.items():
        for obj_name, contents in value.items():
            g.add((rdflib.Literal(obj_name), RDF.type, rdflib.Literal(type_name)))
            for attr_name, value in contents.items():
                interned = intern_object(g, value)
                g.add((rdflib.Literal(obj_name), IDF[attr_name], interned))
    g.bind("idf", IDF)
    return g
