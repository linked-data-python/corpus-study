# Extracted from ktbs/ktbs@4f9f50c770 : lib/ktbs/plugins/virtuoso_sparql.py
# region: <module> (lines 175-200, stratum remove)
# licence of the source repository: see meta.json
from rdflib import BNode, URIRef

if __name__ == "__main__":
    from rdflib import Namespace, Graph, Literal
    from rdflib.collection import Collection

    start_plugin(None)

    EX = Namespace('http://example.org/')
    #store = VSPARQLStore('http://localhost:8890/sparql-auth', 'dba', 'dba')
    g = Graph("VirtuosoS", EX.g)
    g.open("http://localhost:8890/sparql-auth|dba|dba")
    g.remove((None, None, None))
    assert len(g) == 0

    bn = BNode()
    g.add((EX.s, EX.p1, bn))
    g.add((bn, EX.p2, Literal("foo")))
    assert len(g) == 2

    lh = BNode()
    g.add((EX.s, EX.p3, lh))
    lst = Collection(g, lh, list(map(Literal, [1,2,3])))
    assert len(g) == 9

    print((g.serialize(format="turtle", encoding='utf-8').decode('utf-8')))

    g.remove((None, None, None))
