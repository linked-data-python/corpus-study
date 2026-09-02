# Context shim (see meta.json): the helper functions `dquery` calls but
# that are not part of the sampled region -- transcribed VERBATIM from
# matthiasprobst/ontology-utils@668f1b884a : ontolutils/classes/query_util.py
# (split_uri is one line, forwarded from ontolutils/classes/utils.py) --
# so the region executes outside the package. Identical bindings for both
# representations; no logic invented.
from typing import Union

import rdflib


def split_uri(uri: rdflib.URIRef):
    """Split a URIRef into namespace and key. (classes/utils.py::split_uri)"""
    return rdflib.namespace.split_uri(uri)


def _is_type_definition(graph, iri: Union[str, rdflib.URIRef]):
    _sub_query_string = """PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
SELECT DISTINCT ?o WHERE { <%s> rdf:type ?o }""" % iri
    _sub_res = graph.query(_sub_query_string)
    return len(_sub_res) == 1


def _query_by_id(graph, _id: Union[str, rdflib.URIRef], add_type: bool):
    """Query the graph by the id. Return the data as a dictionary."""
    _sub_query_string = """SELECT DISTINCT ?p ?o WHERE { <%s> ?p ?o }""" % _id
    _sub_res = graph.query(_sub_query_string)
    out = {'@id': str(_id)}
    for binding in _sub_res.bindings:
        predicate = binding['p']
        obj = binding['o']

        if predicate == rdflib.RDF.type:
            if add_type:
                out['@type'] = str(obj)
            continue

        _, key = split_uri(predicate)
        if str(_id) == str(obj):
            # would lead to a circular reference. Example for it: "landingPage" and "_id" are the same.
            # in this case, we return the object as a string
            out[key] = str(obj)
        else:
            if key in out:
                if isinstance(out[key], list):
                    out[key].append(process_object(_id, predicate, obj, graph, add_type))
                else:
                    out[key] = [out[key], process_object(_id, predicate, obj, graph, add_type)]
            else:
                out[key] = process_object(_id, predicate, obj, graph, add_type)

    return out


def process_object(
        _id,
        predicate,
        obj: Union[rdflib.URIRef, rdflib.BNode, rdflib.Literal],
        graph,
        add_type):
    """Process the object of a triple."""
    if isinstance(obj, rdflib.Literal):
        if obj.language:
            return f"{obj}@{obj.language}"
        return str(obj)

    if isinstance(obj, rdflib.BNode):
        # find children for predicate with blank node obj
        sub_data = {}
        for (s, p, o) in graph:
            if str(s) == str(obj):
                if isinstance(o, rdflib.Literal):
                    _, key = split_uri(p)
                    sub_data[key] = str(o)
                    continue

                if p == rdflib.RDF.first:
                    # first means we have a collection
                    qs = """PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?item
WHERE {
  ?a rdf:rest*/rdf:first ?item .
}"""
                    list_res = graph.query(qs)

                    _ids = list(set([str(_id[0]) for _id in list_res]))
                    _data = [_query_by_id(graph, _id, add_type) for _id in _ids]
                    return _data

                if p == rdflib.RDF.type and add_type:
                    sub_data["@type"] = str(o)
                else:
                    # may point to another blank node:
                    if isinstance(o, rdflib.BNode):
                        _, key = split_uri(p)
                        if key in sub_data:
                            if isinstance(sub_data[key], list):
                                sub_data[key].append(process_object(_id, p, o, graph, add_type))
                            else:
                                sub_data[key] = [sub_data[key], process_object(_id, p, o, graph, add_type)]
                        else:
                            sub_data[key] = process_object(_id, p, o, graph, add_type)
                    elif str(o).startswith('http'):
                        # it might be a IRI which is defined inside the JSON-LD:
                        _sub_data = process_object(_id, p, o, graph, add_type)
                        if _sub_data:
                            _, key = split_uri(p)
                            sub_data[key] = _sub_data
        if predicate in sub_data:
            return sub_data[predicate]
        return sub_data

    if isinstance(obj, rdflib.URIRef):
        # could be a type definition or a web IRI
        if _is_type_definition(graph, obj):
            if obj == _id:
                return str(obj)
            return _query_by_id(graph=graph, _id=obj, add_type=True)

    return str(obj)


def expand_sparql_res(bindings,
                      graph,
                      add_type: bool,
                      add_context: bool):
    """Expand the SPARQL results. Return a dictionary."""
    out = {}
    for i, binding in enumerate(bindings):
        if isinstance(binding['?id'], rdflib.URIRef):
            _id = str(binding['?id'])
        else:
            _id = binding['?id'].n3()
        if _id not in out:
            out[_id] = {}
            if add_context:
                out[_id] = {'@context': {}}
        p = binding['p'].__str__()
        _, predicate = split_uri(p)

        if predicate == 'type':
            if add_type:
                out[_id]['@type'] = str(binding['o'])
            continue
        if add_context:
            out[_id]['@context'][predicate] = str(p)

        data = process_object(_id, predicate, binding['?o'], graph, add_type)

        if predicate in out[_id]:
            if isinstance(out[_id][predicate], list):
                out[_id][predicate].append(data)
            else:
                out[_id][predicate] = [out[_id][predicate], data]
        else:
            out[_id][predicate] = data

    return out
