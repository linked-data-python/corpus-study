# Extracted from jupyter-naas/abi@3fb7f5304d : libs/naas-abi-marketplace/naas_abi_marketplace/applications/x/apps/x_proxy/hub_test.py
# region: _seed_tweet (lines 112-144, stratum coercion_datatype)
# licence of the source repository: see meta.json
from rdflib import RDF, Dataset, Graph, Literal, Namespace, URIRef
from rdflib.namespace import XSD
_TWEET_GRAPH = "http://ontology.naas.ai/graph/x"
_QUERY = "(drone OR uas) lang:en -is:retweet"
_X = Namespace(_NS)

def _seed_tweet(
    store: "_FakeTripleStore",
    *,
    index: int,
    created: str,
    text: str,
    username: str,
    location: str,
    verified: str = "none",
) -> None:
    """Add one more tweet to the existing search query / result set."""
    g = Graph()
    sq, proc, rs = (
        _X["SearchQuery/q1"],
        _X["SearchRecentTweets/p1"],
        _X["SearchResultSet/r1"],
    )
    tw, au = _X[f"Tweet/{index}"], _X[f"XUser/{username}"]
    g.add((sq, RDF.type, _X.SearchQuery))
    g.add((sq, _X.query_string, Literal(_QUERY)))
    g.add((proc, RDF.type, _X.SearchRecentTweets))
    g.add((proc, _X.usesSearchQuery, sq))
    g.add((proc, _X.producesSearchResult, rs))
    g.add((tw, RDF.type, _X.Tweet))
    g.add((tw, _X.isContainedInSearchResultSet, rs))
    g.add((tw, _X.tweet_created_at, Literal(created, datatype=XSD.dateTime)))
    g.add((tw, _X.full_text, Literal(text)))
    g.add((tw, _X.url, Literal(f"https://x.com/{username}/status/{index}")))
    g.add((tw, _X.isAuthoredBy, au))
    g.add((au, _X.username, Literal(username)))
    g.add((au, _X.user_location, Literal(location)))
    g.add((au, _X.verified_type, Literal(verified)))
    store.insert_graph(g, _TWEET_GRAPH)
