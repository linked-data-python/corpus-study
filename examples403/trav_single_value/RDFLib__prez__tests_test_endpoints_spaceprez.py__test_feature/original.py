# Extracted from RDFLib/prez@421ee0a9fe : tests/test_endpoints_spaceprez.py
# region: test_feature (lines 28-37, stratum trav_single_value)
# licence of the source repository: see meta.json
from rdflib import Graph, URIRef
from rdflib.namespace import DCAT, GEO, RDF

def test_feature(client, a_feature_link):
    r = client.get(f"{a_feature_link}?_mediatype=text/turtle")
    g_text = r.text
    response_graph = Graph().parse(data=g_text)
    expected_response_1 = (
        URIRef("https://example.com/spaceprez/Feature1"),
        RDF.type,
        GEO.Feature,
    )
    assert next(response_graph.triples(expected_response_1))
