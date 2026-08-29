# Extracted from semantic-systems/coypu-mapping-generation@61a6620ea9 : util/rdf2csv.py
# region: _resolve_geom (lines 96-113, stratum sparql_interpolated)
# licence of the source repository: see meta.json
from typing import Union, Tuple
from rdflib import Graph, URIRef, IdentifiedNode, BNode
from rdflib.term import Node, Literal

def _resolve_geom(geom_uri: Node, g: Graph) -> Tuple[float, float]:
    query_results = g.query(
        f'SELECT ?wkt '
        f'WHERE {{ '
        f'  <{str(geom_uri)}> <http://www.opengis.net/ont/geosparql#asWKT> ?wkt '
        f'}}')

    for result in query_results:
        # there should at most be one result

        # get first projection value, i.e., ?wkt
        result_literal = result[0]
        lat, lon = _parse_coordinates(str(result_literal))

    if len(query_results) == 0:
        raise Exception(f'No coordinates found for {geom_uri}')

    return lat, lon
