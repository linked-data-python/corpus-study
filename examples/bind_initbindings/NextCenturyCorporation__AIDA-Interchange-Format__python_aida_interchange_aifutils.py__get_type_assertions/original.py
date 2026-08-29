# Extracted from NextCenturyCorporation/AIDA-Interchange-Format@1197e7adef : python/aida_interchange/aifutils.py
# region: get_type_assertions (lines 991-1002, stratum bind_initbindings)
# licence of the source repository: see meta.json
# (added to make the region executable: the real file imports it at the top,
# `from rdflib.plugins.sparql import prepareQuery`, alongside many other
# imports the region does not need -- see meta.json)
from rdflib.plugins.sparql import prepareQuery

_TYPE_QUERY = prepareQuery("""SELECT ?typeAssertion WHERE {
  ?typeAssertion a rdf:Statement .
  ?typeAssertion rdf:predicate rdf:type .
  ?typeAssertion rdf:subject ?typedObject .
  }
  """)

def get_type_assertions(g, typed_object):
    """
    Retrieve all type assertions from an entity.

    :param rdflib.graph.Graph g: The underlying RDF model
    :param rdflib.term.URIRef typed_object: The entity from which to retrieve
        type assertions
    :returns: A list of type assertions for the specified entity
    :rtype: list
    """
    query_result = g.query(_TYPE_QUERY, initBindings={'typedObject': typed_object})
    return [x for (x,) in query_result]
