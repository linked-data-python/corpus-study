# Extracted from pangenome/spodgi@6d7d944f38 : test/test_select.py
# region: test_count_all (lines 28-37, stratum sparql_literal)
# licence of the source repository: see meta.json
from rdflib.store import Store
from rdflib import Graph
from rdflib import plugin

def test_count_all():
    plugin.register('OdgiStore', Store, 'spodgi.OdgiStore', 'OdgiStore')
    s = plugin.get('OdgiStore', Store)(base="http://example.org/test/")
    spodgi = Graph(store=s)
    spodgi.open('./test/t.odgi', create=False)
    for r in spodgi.query('SELECT (count(*) as ?count) WHERE {?s ?p ?o}'):
        assert r[0].value > 195

    spodgi.close()
    assert True
