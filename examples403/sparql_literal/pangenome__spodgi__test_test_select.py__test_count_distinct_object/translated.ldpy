# Extracted from pangenome/spodgi@6d7d944f38 : test/test_select.py
# region: test_count_distinct_object (lines 77-132, stratum sparql_literal)
# licence of the source repository: see meta.json
from rdflib.store import Store
from rdflib import Graph
from rdflib import plugin

def test_count_distinct_object():
    plugin.register('OdgiStore', Store, 'spodgi.OdgiStore', 'OdgiStore')
    s = plugin.get('OdgiStore', Store)(base="http://example.org/test/")
    spodgi = Graph(store=s)
    spodgi.open('./test/t.odgi', create=False)

    for r in spodgi.query('''PREFIX faldo:<http://biohackathon.org/resource/faldo#>
                          SELECT (count(distinct ?o) as ?count) WHERE {?s faldo:reference ?o}'''):
        assert r[0].value == 1
    for r in spodgi.query('''PREFIX faldo:<http://biohackathon.org/resource/faldo#>
                          SELECT (count(distinct ?o) as ?count) WHERE {?s faldo:begin ?o}'''):
            assert r[0].value == 10
    for r in spodgi.query('''PREFIX faldo:<http://biohackathon.org/resource/faldo#>
                              SELECT (count(distinct ?o) as ?count) WHERE {?s faldo:end ?o}'''):
        assert r[0].value == 10
    for r in spodgi.query('''PREFIX faldo:<http://biohackathon.org/resource/faldo#>
                        PREFIX vg:<http://biohackathon.org/resource/vg#>
                        SELECT (count(distinct ?o) as ?count) WHERE {?s vg:rank ?o}'''):
        assert r[0].value == 10
    for r in spodgi.query('''PREFIX faldo:<http://biohackathon.org/resource/faldo#>
                        PREFIX vg:<http://biohackathon.org/resource/vg#>
                        SELECT (count(distinct ?o) as ?count) WHERE {?s vg:node ?o}'''):
        assert r[0].value == 10
    for r in spodgi.query('''PREFIX faldo:<http://biohackathon.org/resource/faldo#>
                        PREFIX vg:<http://biohackathon.org/resource/vg#>
                        SELECT (count(distinct ?o) as ?count) WHERE {?s vg:node ?o}'''):
        assert r[0].value == 10
    for r in spodgi.query('''PREFIX faldo:<http://biohackathon.org/resource/faldo#>
                        PREFIX vg:<http://biohackathon.org/resource/vg#>
                        SELECT (count(distinct ?o) as ?count) WHERE {?s vg:links ?o}'''):
        assert r[0].value == 14
    for r in spodgi.query('''PREFIX faldo:<http://biohackathon.org/resource/faldo#>
                        PREFIX vg:<http://biohackathon.org/resource/vg#>
                        SELECT (count(distinct ?o) as ?count) WHERE {?s vg:linksForwardToForward ?o}'''):
        assert r[0].value == 14
    for r in spodgi.query('''PREFIX faldo:<http://biohackathon.org/resource/faldo#>
                        PREFIX vg:<http://biohackathon.org/resource/vg#>
                        SELECT (count(distinct ?o) as ?count) WHERE {?s faldo:position ?o}'''):
        assert r[0].value == 11
    for r in spodgi.query('''PREFIX faldo:<http://biohackathon.org/resource/faldo#>
                        PREFIX vg:<http://biohackathon.org/resource/vg#>
                        SELECT distinct ?s 
                        WHERE {{?s a faldo:Position }UNION {?s a faldo:ExactPosition }}'''):
        print(r[0], type(r[0]))

    for r in spodgi.query('''PREFIX faldo:<http://biohackathon.org/resource/faldo#>
                        PREFIX vg:<http://biohackathon.org/resource/vg#>
                        SELECT (count(distinct ?s) as ?count) 
                        WHERE {{?s a faldo:Position }UNION {?s a faldo:ExactPosition }}'''):
        assert r[0].value == 11
    # for r in spodgi.query('SELECT ?p (count(distinct ?o) as ?count) WHERE {?s ?p ?o} GROUP BY ?p'):
    #     print(r[0], ':', r[1])


    spodgi.close()
    assert True
